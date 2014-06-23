"""
    Django Async models.
"""
from datetime import datetime, timedelta
from django.db import models, transaction
# No name 'sha1' in module 'hashlib'
# pylint: disable=E0611
from hashlib import sha1
from simplejson import dumps, loads
from traceback import format_exc

from async import _logger
from async.utils import object_at_end_of_path, non_unicode_kwarg_keys


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
        help_text = "If not set, will be executed ASAP")
    started = models.DateTimeField(null=True, blank=True)
    executed = models.DateTimeField(null=True, blank=True)


    def __unicode__(self):
        # __unicode__: Instance of 'bool' has no 'items' member
        # pylint: disable=E1103
        args = ', '.join([repr(s) for s in loads(self.args)] +
            ['%s=%s' % (k, repr(v)) for k, v in loads(self.kwargs).items()])
        return u'%s(%s)' % (self.name, args)

    def save(self, *a, **kw):
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
            self.started = datetime.now()
            self.save()
        transaction.commit_on_success(start)()
        try:
            _logger.info("%s %s", self.id, unicode(self))
            args = loads(self.args)
            kwargs = non_unicode_kwarg_keys(loads(self.kwargs))
            function = object_at_end_of_path(self.name)
            _logger.debug(u"%s resolved to %s" % (self.name, function))
            result = transaction.commit_on_success(function)(*args, **kwargs)
        except Exception as exception:
            self.started = None
            errors = 1 + self.errors.count()
            self.scheduled = (datetime.now() +
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
            self.executed = datetime.now()
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

