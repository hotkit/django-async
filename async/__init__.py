"""
    Django Async implementation.
"""


def schedule(*a, **kw): # pragma: no cover
    """Wrapper for async.schedule.schedule that allow coverage.
    """
    # Redefining name 'schedule' from outer scope
    # pylint: disable=W0621
    from async.api import schedule
    return schedule(*a, **kw)

