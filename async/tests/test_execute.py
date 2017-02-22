"""
    Tests for task execution.
"""
from django.contrib.auth.models import User
try:
    from django.test import TransactionTestCase
except ImportError:
    from django.test import TestCase as TransactionTestCase

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
    for name in a:
        User(username=name).save()
    assert kw.get('assert', True)
    return kw.get('result', None)


class _class(object):
    """Test class holder.
    """
    @classmethod
    def class_method(cls, *a, **kw):
        """Class method so we can be sure these work.
        """
        # Using the global statement
        # pylint: disable = W0603
        global _EXECUTED
        _EXECUTED = (a, kw)


class TestExecution(TransactionTestCase):
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
        job = schedule(_function,
            args=['async-test-user'], kwargs={'result': 'something'})
        self.assertEqual(job.execute(), "something")
        self.assertEqual(_EXECUTED,
            (('async-test-user',), {'result': 'something'}))
        self.assertEqual('"something"', job.result)
        self.assertIsNotNone(job.executed)
        self.assertLess(job.started, job.executed)
        self.assertEqual(
            User.objects.filter(username='async-test-user').count(), 1)

    def test_error_recording(self):
        """Make sure that if there is an error in the function it is dealt
        with properly.
        """
        job = Job.objects.get(
            pk=schedule(_function,
                args=['async-test-user'], kwargs={'assert': False}).pk)
        self.assertEqual(job.errors.count(), 0)
        with self.assertRaises(AssertionError):
            job.execute()
        self.assertEqual(_EXECUTED, (('async-test-user',), {'assert': False}))
        job = Job.objects.get(pk=job.pk)
        self.assertEqual(job.errors.count(), 1)
        error = job.errors.all()[0]
        self.assertIn('AssertionError', error.exception)
        self.assertIn('async/tests/test_execute.py', error.traceback)
        self.assertIsNotNone(job.scheduled)
        self.assertEqual(
            User.objects.filter(username='async-test-user').count(), 0)

    def test_class_method_works(self):
        """Make sure that we can execute a class method.
        """
        job = schedule(_class.class_method)
        job.execute()
        self.assertIsNotNone(job.executed)
