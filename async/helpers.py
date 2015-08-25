from functools import wraps
from async.models import Job


def clear_queue(f):
    """
    Delete all jobs before run the function
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        Job.objects.all().delete()
        return f(*args, **kwargs)
    return wrapper

