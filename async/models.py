"""
    Django Async models.
"""
from django.db import models
from simplejson import loads


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


class Error(models.Model):
    """
        Recorded when an error happens during execution of a job.
    """
    job = models.ForeignKey(Job)
    executed = models.DateTimeField(auto_now_add=True)
    exception = models.TextField()
    traceback = models.TextField()

