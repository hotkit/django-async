"""
    Async Slumber server configuration
"""
from slumber import configure

from async.models import Job, Group
from async.slumber_operations import Health, Schedule, Progress


configure(Job, operations_extra=[
    (Health, 'health'),
    (Schedule, 'schedule'),
])

configure(Group, operations_extra=[
    (Progress, 'progress'),
])

