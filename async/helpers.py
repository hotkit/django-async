"""
    Helper functions.
"""
from functools import wraps
from async.models import Job


def clear_queue(func):
    """
    Delete all jobs before run the function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        A wrapper function
        """
        Job.objects.all().delete()
        return func(*args, **kwargs)
    return wrapper

