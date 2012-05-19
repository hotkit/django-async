"""
    Tests for task execution.
"""
from django.test import TestCase

from async import schedule
from async.models import Job


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
    return kw.get('result', None)


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
        job = schedule(_function, kwargs={'result': 'something'})
        job()
        self.assertEqual(_EXECUTED, ((), {'result': 'something'}))
        self.assertEqual('"something"', job.result)
        self.assertIsNotNone(job.executed)

    def test_error_recording(self):
        """Make sure that if there is an error in the function it is dealt
        with properly.
        """
        job = Job.objects.get(
            pk=schedule(_function, kwargs={'assert': False}).pk)
        self.assertEqual(job.errors.count(), 0)
        with self.assertRaises(AssertionError):
            job()
        self.assertEqual(_EXECUTED, ((), {'assert': False}))
        job = Job.objects.get(pk=job.pk)
        self.assertEqual(job.errors.count(), 1)
        error = job.errors.all()[0]
        self.assertIn('AssertionError', error.exception)
        self.assertIn('django_1_3/async/tests/test_execute.py', error.traceback)
        self.assertIsNotNone(job.scheduled)
