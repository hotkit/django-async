"""
    Tests for the Django management commands.
"""
from django.core import management
from django.test import TestCase
try:
    # No name 'timezone' in module 'django.utils'
    # pylint: disable=E0611
    from django.utils import timezone as datetime
except ImportError:
    from datetime import datetime
from mock import patch

from async import schedule
from async.api import health, deschedule
from async.models import Job


# Using the global statement
# pylint: disable = W0603


ORDER = None
def _dummy(order=None, error=None):
    """Basic dummy function we can use to test the queue execution.
    """
    if order:
        ORDER.append(order)
    if error:
        raise Exception(error)


class TestFlushQueue(TestCase):
    """Test the flush_queue management command.
    """
    def test_empty_queue(self):
        """Make sure we don't get any errors if the queue is empty.
        """
        management.call_command('flush_queue')
        self.assertEqual(Job.objects.all().count(), 0)

    def test_asap_tasks(self):
        """Make sure that tasks scheduled for immediate execution
        are run.
        """
        schedule(_dummy)
        self.assertEqual(Job.objects.filter(executed=None).count(), 1)
        management.call_command('flush_queue')
        self.assertEqual(Job.objects.filter(executed=None).count(), 0)

    def test_queue_fails_on_error(self):
        """Make sure that the queue flushing stops on the first error.
        """
        schedule(_dummy, kwargs={'error': "Error"})
        schedule(_dummy)
        self.assertEqual(Job.objects.filter(executed=None).count(), 2)
        with self.assertRaises(Exception):
            management.call_command('flush_queue')
        self.assertEqual(Job.objects.filter(executed=None).count(), 2)
        management.call_command('flush_queue')
        self.assertEqual(Job.objects.filter(executed=None).count(), 1)

    def test_scheduled_runs_first_when_added_first(self):
        """Make sure that the scheduled job is always run first.
        """
        global ORDER
        ORDER = []
        schedule(_dummy, args=[1], run_after=datetime.now())
        schedule(_dummy, args=[2])
        management.call_command('flush_queue')
        self.assertEqual(ORDER, [1, 2])

    def test_scheduled_runs_first_when_added_last(self):
        """Make sure that the scheduled job is always run first.
        """
        global ORDER
        ORDER = []
        schedule(_dummy, args=[2])
        schedule(_dummy, args=[1], run_after=datetime.now())
        management.call_command('flush_queue')
        self.assertEqual(ORDER, [1, 2])

    def test_scheduled_runs_last_when_has_higher_priority(self):
        """The lowest priority scheduled job runs before the highest
        priority non-scheduled job.
        """
        global ORDER
        ORDER = []
        schedule(_dummy, args=[1], priority=5)
        schedule(_dummy, args=[2], priority=1, run_after=datetime.now())
        management.call_command('flush_queue')
        self.assertEqual(ORDER, [1, 2])

    def test_flush_queue_with_jobs_limit(self):
        """Make sure that the number of job run is the same
        as the input jobs limit.
        """
        for _ in range(5):
            schedule(_dummy)
        management.call_command('flush_queue', jobs=2)
        self.assertEqual(Job.objects.filter(executed=None).count(), 3)

    def test_flush_queue_without_jobs_limit_limit_at_300_by_default(self):
        """Make sure that the number of job run by default is 300.
        """
        for _ in range(305):
            schedule(_dummy)
        management.call_command('flush_queue')
        self.assertEqual(Job.objects.filter(executed=None).count(), 5)

    def test_flush_queue_with_cancelled_jobs__should_not_be_executed(self):
        """Make sure that the number of job run by default is 300.
        """
        for _ in range(5):
            job = schedule(_dummy)
            deschedule(job.name)
        management.call_command('flush_queue')
        self.assertEqual(Job.objects.filter(executed=None).count(), 5)
        self.assertEqual(Job.objects.filter(cancelled=None).count(), 0)


class TestHealth(TestCase):
    """Make sure the health command runs without any errors.
    """
    def test_health(self):
        """Excecute command.
        """
        print( health())
        print( management.call_command('queue_health'))
        with patch(
                'async.management.commands.queue_health.dumps',
                lambda x: self.assertEqual(x, health())):
            management.call_command('queue_health')



    def test_health_with_options(self):
        """Excecute command.
        """
        with patch(
                'async.management.commands.queue_health.dumps',
                lambda x: self.assertEqual(x, health())):
            management.call_command('queue_health', algorithm='rough')
        self.assertRaises(BaseException, management.call_command,
                          'queue_health', algorithm='hello')
