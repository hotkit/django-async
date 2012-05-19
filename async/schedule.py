"""
    Schedule the execution of an async task.
"""
from simplejson import dumps


def schedule(function, args = None, kwargs = None,
        run_after= None, meta = None):
    """Schedule a tast for execution.
    """
    from async.models import Job # Don't want to import from __init__
    job = Job(
        name=function, args=dumps(args or []), kwargs=dumps(kwargs or {}),
        meta=dumps(meta or {}), retried=0, notes='', scheduled=run_after)
    job.save()
    return job
