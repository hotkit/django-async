"""
    Tests for task execution.
"""
from django.test import TestCase

from async import schedule


# Redefining name '_EXECUTED' from outer scope
# pylint: disable = W0621
_EXECUTED = None

def _function(*a, **kw):
    """A simple test function.
    """
    # Using the global statement
    # pylint: disable = W0603
    global _EXECUTED
    _EXECUTED = (a, kw)


class TestExecution(TestCase):
    """Test that execution of a job works correctly in all circumstances.
    """
    def setUp(self):
        # Using the global statement
        # pylint: disable = W0603
        global _EXECUTED
        _EXECUTED = None

    def test_simple(self):
        """Execute a basic function.
        """
        schedule(_function)()
        self.assertEqual(_EXECUTED, ((), {}))
