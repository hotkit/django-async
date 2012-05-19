"""
    Schedule the execution of an async task.
"""


def schedule(function, args = None, kwargs = None,
        run_after= None, meta = None):
    """Schedule a tast for execution.
    """
    from async.models import Job # Don't want to import from __init__
    return Job.objects.create()
