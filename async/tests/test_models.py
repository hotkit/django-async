"""
    Testing that models work properly.
"""
from django.test import TestCase

from async import schedule
from async.models import Job


class TestJob(TestCase):
    """Make sure the basic model features work properly.
    """
    def test_model_creation(self):
        schedule('async.cron')
        self.assertEqual(Job.objects.all().count(), 1)
