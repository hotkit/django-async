"""
    Schedule the execution of an async task.
"""
from simplejson import dumps

from async.utils import full_name


def schedule(function, args = None, kwargs = None,
        run_after= None, meta = None):
    """Schedule a tast for execution.
    """
    from async.models import Job # Don't want to import from __init__
    job = Job(
        name=full_name(function),
            args=dumps(args or []), kwargs=dumps(kwargs or {}),
        meta=dumps(meta or {}), scheduled=run_after)
    job.save()
    return job
