"""
    Django Async models.
"""
from datetime import  timedelta
from django.db import models, transaction
try:
    # No name 'timezone' in module 'django.utils'
    # pylint: disable=E0611
    from django.utils import timezone
except ImportError:
    from datetime import datetime as timezone
# No name 'sha1' in module 'hashlib'
# pylint: disable=E0611
from hashlib import sha1
from simplejson import dumps, loads
from traceback import format_exc

from async.logger import _logger
from async.utils import object_at_end_of_path, non_unicode_kwarg_keys

from django.core.exceptions import ValidationError


class Group(models.Model):
    """
        A group for jobs that need to be executed.
    """
    reference = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s' % self.reference

    def save(self, *args, **kwargs):
        # We can't create a new group with that reference
        # if the old group still have jobs that havn't executed.
        if Job.objects.filter(
                group__reference=self.reference,
                executed__isnull=True
        ).count() > 0:
            raise ValidationError(
                "There have group reference [%s] has unexecuted jobs." %
                    self.reference)
        return super(Group, self).save(*args, **kwargs)


class Job(models.Model):
    """
        An asynchronous task that is to be executed.
    """
    name = models.CharField(max_length=100, blank=False)
    args = models.TextField()
    kwargs = models.TextField()
    meta = models.TextField()
    result = models.TextField(blank=True)

    priority = models.IntegerField()
    identity = models.CharField(max_length=100, blank=False, db_index=True)

    added = models.DateTimeField(auto_now_add=True)
    scheduled = models.DateTimeField(null=True, blank=True,
        help_text="If not set, will be executed ASAP")
    started = models.DateTimeField(null=True, blank=True)
    executed = models.DateTimeField(null=True, blank=True)
    cancelled = models.DateTimeField(null=True, blank=True)

    group = models.ForeignKey(Group, related_name='jobs',
        null=True, blank=True)

    def __unicode__(self):
        # __unicode__: Instance of 'bool' has no 'items' member
        # pylint: disable=E1103
        args = ', '.join([repr(s) for s in loads(self.args)] +
            ['%s=%s' % (k, repr(v)) for k, v in loads(self.kwargs).items()])
        return u'%s(%s)' % (self.name, args)

    def save(self, *a, **kw):
        # Stop us from cheating by adding the new jobs to the old group.
        # Checking if group obj got passed and current job is not in that group
        if self.group and self not in self.group.jobs.all():
            # Cannot add current job to latest group that have an executed job.
            if self.group.jobs.filter(executed__isnull=False).count() > 0:
                raise ValidationError(
                    "Cannot add job [%s] to group [%s] because this group "
                        "has executed jobs." %
                            (self.name, self.group.reference))
        self.identity = sha1(unicode(self)).hexdigest()
        return super(Job, self).save(*a, **kw)

    def execute(self, **_meta):
        """
            Run the job using the specified meta values to control the
            execution.
        """
        def start():
            """Record the start time for the job.
            """
            self.started = timezone.now()
            self.save()
        transaction.commit_on_success(start)()
        try:
            _logger.info("%s %s", self.id, unicode(self))
            args = loads(self.args)
            kwargs = non_unicode_kwarg_keys(loads(self.kwargs))
            function = object_at_end_of_path(self.name)
            _logger.debug(u"%s resolved to %s" % (self.name, function))
            result = transaction.commit_on_success(function)(*args, **kwargs)
        except Exception, exception:
            self.started = None
            errors = 1 + self.errors.count()
            self.scheduled = (timezone.now() +
                timedelta(seconds=60 * pow(errors, 1.6)))
            self.priority = self.priority - 1
            _logger.error(
                "Job failed. Rescheduled for %s after %s error(s). "
                    "New priority is %s",
                self.scheduled, errors, self.priority)
            def record():
                """Local function allows us to wrap these updates into a
                transaction.
                """
                Error.objects.create(job=self, exception=repr(exception),
                    traceback=format_exc())
                self.save()
            transaction.commit_on_success(record)()
            raise
        else:
            self.executed = timezone.now()
            self.result = dumps(result)
            self.save() # Single SQL statement so no need for transaction
            return result


class Error(models.Model):
    """
        Recorded when an error happens during execution of a job.
    """
    job = models.ForeignKey(Job, related_name='errors')
    executed = models.DateTimeField(auto_now_add=True)
    exception = models.TextField()
    traceback = models.TextField()

    def __unicode__(self):
        return u'%s : %s' % (self.executed, self.exception)

