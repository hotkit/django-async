"""
    Schedule the execution of an async task.
"""
from async.models import Job


def schedule(function, args = None, kwargs = None,
        run_after= None, meta = None):
    """Schedule a tast for execution.
    """
    return Job.objects.create()
