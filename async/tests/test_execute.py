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
    assert kw.get('assert', True)


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

    def test_error_recording(self):
        """Make sure that if there is an error in the function it is dealt
        with properly.
        """
        job = schedule(_function, kwargs={'assert': False})
        self.assertEqual(job.errors.count(), 0)
        with self.assertRaises(AssertionError):
            job()
        self.assertEqual(_EXECUTED, ((), {'assert': False}))
        self.assertEqual(job.errors.count(), 1)
        error = job.errors.all()[0]
        self.assertIn('AssertionError', error.exception)
        self.assertIn('django_1_3/async/tests/test_execute.py', error.traceback)
        self.assertIsNotNone(job.scheduled)
