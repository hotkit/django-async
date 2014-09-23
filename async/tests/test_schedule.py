"""
    Test the schedule API.
"""
from django.test import TestCase

from async import schedule


def _example():
    """An example function that can be used for testing purposes.
    """
    pass


class TestSchedule(TestCase):
    """Make sure that scheduling works correctly.
    """
    def test_schedule_by_name(self):
        """We must be able to schedule a job by giving its name.
        """
        job = schedule('async.tests.test_schedule._example')
        self.assertEqual(job.name, 'async.tests.test_schedule._example')

    def test_schedule_by_function(self):
        """We must be able to schedule a job by giving a function.
        """
        job = schedule(_example)
        # Different versions of Django will import this file differently
        self.assertTrue(job.name.endswith(
            'async.tests.test_schedule._example'))

    def test_schedule_in_group(self):
        """Make sure that a group is created if it doesn't already exist.
        """
        job = schedule(_example, group='test_schedule_in_group')
        self.assertEqual(job.group.reference, 'test_schedule_in_group')

