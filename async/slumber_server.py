"""
    Async Slumber server configuration
"""
from slumber import configure

from async.models import Job
from async.slumber_operations import Schedule


configure(Job, operations_extra=[
    (Schedule, 'schedule')])

