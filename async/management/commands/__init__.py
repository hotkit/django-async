"""
    Django Async management commands.
"""

try:
    from slumber.server.meta import applications
    applications()
except ImportError:
    pass
