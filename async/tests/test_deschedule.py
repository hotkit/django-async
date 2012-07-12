"""
    Test the deschedule API.
"""
from django.test import TestCase

from async import schedule
from async.api import deschedule
from async.models import Job


def _example(*a, **kw):
    """An example function that can be used for testing purposes.
    """
    pass


class TestDeschedule(TestCase):
    """Make sure that descheduling works correctly.
    """
    def test_deschedule_by_name(self):
        """We must be able to schedule a job by giving its name.
        """
        job = schedule('async.tests.test_deschedule._example')
        self.assertEqual(job.name, 'async.tests.test_deschedule._example')
        deschedule('async.tests.test_deschedule._example')
        job = Job.objects.get(pk=job.pk)
        self.assertIsNotNone(job.executed)

    def test_deschedule_by_function(self):
        """We must be able to schedule a job by giving a function.
        """
        job = schedule(_example)
        # Different versions of Django will import this file differently
        self.assertTrue(job.name.endswith(
            'async.tests.test_deschedule._example'))
        deschedule(_example)
        job = Job.objects.get(pk=job.pk)
        self.assertIsNotNone(job.executed)
