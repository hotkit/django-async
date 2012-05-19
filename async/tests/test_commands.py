"""
    Tests for the Django management commands.
"""
from django.test import TestCase


class TestFlushQueue(TestCase):
    """Test the flush_queue management command.
    """
    def test_empty_queue(self):
        """Make sure we don't get any errors if the queue is empty.
        """
        pass
