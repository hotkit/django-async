from async_exec.api import schedule
from async_exec.models import Job
from async_exec.tests.function_for_test import sample_function, function_that_takes_job 
from datetime import datetime
from django.test import TestCase

class TestSchedule(TestCase):
    def test_schedule_asap(self):
        job = schedule(sample_function)
        self.assertTrue(job.id)

    def test_schedule_at_time(self):
        job = schedule(sample_function, schedule_time = datetime.now())
        self.assertTrue(job.scheduled)

    def test_schedule_with_params(self):
        job = schedule(sample_function, args = ['Lady', 'Gaga'], kwargs = {'song': 'Paparazzi'})
        self.assertTrue(job.args)
        self.assertTrue(job.kwargs)
        
    def test_schedule_with_params_as_job(self):
        job = schedule(function_that_takes_job, kwargs = {'job': 'abc'})
        self.assertEqual('{"job": "abc"}', job.kwargs)

