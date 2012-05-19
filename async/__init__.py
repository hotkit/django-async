"""
    Django Async implementation.
"""
import logging as _logger


def schedule(*a, **kw):
    """Wrapper for async.schedule.schedule that allow coverage.
    """
    # Redefining name 'schedule' from outer scope
    # pylint: disable=W0621
    from async.api import schedule
    return schedule(*a, **kw)
