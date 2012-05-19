"""
    Django Async models.
"""
from django.db import models


class Job(models.Model):
    """
        An asynchronous task that is to be executed.
    """
    module = models.CharField(max_length=100, blank=False)
    name = models.CharField(max_length=100, blank=False)
    args = models.TextField()
    kwargs = models.TextField()
    meta = models.TextField()

    retried = models.IntegerField()
    notes = models.TextField()

    scheduled = models.DateTimeField(null=True, blank=True,
        help_text = "If not set, will be executed ASAP")
    executed = models.DateTimeField(null=True, blank=True)

