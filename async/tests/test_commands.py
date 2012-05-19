"""
    Tests for the Django management commands.
"""
from django.core import management
from django.test import TestCase

from async.models import Job


class TestFlushQueue(TestCase):
    """Test the flush_queue management command.
    """
    def test_empty_queue(self):
        """Make sure we don't get any errors if the queue is empty.
        """
        management.call_command('flush_queue')
        self.assertEqual(Job.objects.all().count(), 0)
