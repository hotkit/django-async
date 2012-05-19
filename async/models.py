"""
    Django Async models.
"""
from datetime import datetime, timedelta
from django.db import models
from simplejson import loads
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

    retried = models.IntegerField()
    notes = models.TextField()

    added = models.DateTimeField(auto_now_add=True)
    scheduled = models.DateTimeField(null=True, blank=True,
        help_text = "If not set, will be executed ASAP")
    executed = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        # __unicode__: Instance of 'bool' has no 'items' member
        # pylint: disable=E1103
        args = ', '.join([repr(s) for s in loads(self.args)] +
            ['%s=%s' % (k, repr(v)) for k, v in loads(self.kwargs).items()])
        return u'%s(%s)' % (self.name, args)

    def __call__(self, **meta):
        _logger.info("%s %s", self.id, unicode(self))
        try:
            args = loads(self.args)
            kwargs = non_unicode_kwarg_keys(loads(self.kwargs))
            function = object_at_end_of_path(self.name)
            _logger.debug(u"%s resolved to %s" % (self.name, function))
            self.retried += 1
            function(*args, **kwargs)
        except Exception, exception:
            self.scheduled = (datetime.now() +
                timedelta(seconds=4 ** self.retried))
            def record():
                """Local function allows us to wrap these updates into a
                transaction.
                """
                Error.objects.create(job=self, exception=repr(exception),
                    traceback=format_exc())
                self.save()
            record()
            raise


class Error(models.Model):
    """
        Recorded when an error happens during execution of a job.
    """
    job = models.ForeignKey(Job, related_name='errors')
    executed = models.DateTimeField(auto_now_add=True)
    exception = models.TextField()
    traceback = models.TextField()

