"""
    Async Slumber server configuration
"""
try:
    from slumber import configure
except ImportError:  # pragma: no cover
    pass

from async.models import Job, Group
from async.slumber_operations import Health, Schedule, Progress


configure(Job, operations_extra=[
    (Health, 'health'),
    (Schedule, 'schedule'),
])

configure(Group, operations_extra=[
    (Progress, 'progress'),
])

