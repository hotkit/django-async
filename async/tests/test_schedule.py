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
        job = schedule('example.function')
        self.assertEqual(job.name, 'example.function')

    def test_schedule_by_function(self):
        """We must be able to schedule a job by giving a function.
        """
        job = schedule(_example)
        self.assertEqual(job.name,
            'django_1_3.async.tests.test_schedule._example')
