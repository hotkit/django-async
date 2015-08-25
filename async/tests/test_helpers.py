from async import schedule
from async.helpers import clear_queue
from async.models import Job
from django.test import TestCase


def _example():
    """An example function that can be used for testing purposes.
    """
    pass


class TestClearQueue(TestCase):
    def setUp(self):
        schedule('async.tests.test_schedule._example')
        schedule('async.tests.test_schedule._example')
        schedule('async.tests.test_schedule._example')

    def test_run_without_decorator(self):
        self.assertEqual(Job.objects.count(), 3)

    @clear_queue
    def test_clear_job(self):
        self.assertEqual(Job.objects.count(), 0)

