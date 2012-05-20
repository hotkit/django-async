"""
    Tests for the Django management commands.
"""
from django.core import management
from django.test import TestCase
from mock import patch

from async import schedule
from async.api import health
from async.models import Job


def _dummy(error=None):
    """Basic dummy function we can use to test the queue execution.
    """
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
        schedule(_dummy, "Error")
        schedule(_dummy)
        self.assertEqual(Job.objects.filter(executed=None).count(), 2)
        with self.assertRaises(Exception):
            management.call_command('flush_queue')
        self.assertEqual(Job.objects.filter(executed=None).count(), 2)
        management.call_command('flush_queue')
        self.assertEqual(Job.objects.filter(executed=None).count(), 1)


class TestHealth(TestCase):
    """Make sure the health command runs without any errors.
    """
    def test_health(self):
        """Excecute command.
        """
        with patch(
                'async.management.commands.queue_health.dumps',
                lambda x: self.assertEqual(x, health())):
            management.call_command('queue_health')

