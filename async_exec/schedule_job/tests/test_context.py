from async_exec.schedule_job.context import ScheduleJob
from async_exec.tests.function_for_test import sample_function, function_that_takes_job
from async_exec.models import Job
from datetime import datetime
from django.test import TestCase

class TestScheduleJob(TestCase):
    def setUp(self):
        self.job = Job()

    def test_job_is_persisted(self):
        with ScheduleJob(None, self.job, sample_function) as context:
            self.assertTrue(context.job.id)
        
    def test_successfully_schedule_job_with_no_scheduled_time(self):
        with ScheduleJob(None, self.job, sample_function) as context:
            self.assertEqual(None, context.job.scheduled)

    def test_successfully_schedule_job_with_scheduled_time(self):
        scheduled_time = datetime.now()
        with ScheduleJob(scheduled_time, self.job, sample_function) as context:
            self.assertEqual(scheduled_time, context.job.scheduled)
        
    def test_successfully_schedule_job_with_kwargs(self):
        """
        Scenario:
            trying the schedule the line below
            sample_function(name = 'John')
        Expected:
            the kwargs are persisted
        """
        with ScheduleJob(None, self.job, 
                 sample_function, kwargs = {'name': 'John'}) as context:
            self.assertEqual('{"name": "John"}', context.job.kwargs)

