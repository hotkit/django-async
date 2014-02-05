"""
    Async Slumber server configuration
"""
from slumber import configure

from async.models import Job, Group
from async.slumber_operations import Schedule, Progress


configure(Job, operations_extra=[
    (Schedule, 'schedule')
])

configure(Group, operations_extra=[
    (Progress, 'progress'),
])

