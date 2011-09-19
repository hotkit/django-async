from datetime import datetime
from django.test import TestCase
from async_exec.schedule_job.context import ScheduleJob
from async_exec.schedule_job.tests.function_for_test import sample_function
from async_exec.models import Job

class TestScheduleJob(TestCase):
    def test_successfully_schedule_job_with_no_scheduled_time(self):
        job = Job()
        with ScheduleJob(None, job, sample_function) as schedule_job:
            # Conditions may not change in here because post conditions are met! 
            self.assertTrue(schedule_job.job.id)
            self.assertEqual(None, schedule_job.job.scheduled)

    def test_successfully_schedule_job_with_scheduled_time(self):
        job = Job()
        scheduled_time = datetime.now()
        with ScheduleJob(scheduled_time, job, sample_function) as schedule_job:
            # Conditions may not change in here because post conditions are met! 
            self.assertEqual(scheduled_time, schedule_job.job.scheduled)
        
    def test_successfully_schedule_job_with_kwargs(self):
        job = Job()
        with ScheduleJob(None, job, sample_function, name = 'John') as schedule_job:
            # Conditions may not change in here because post conditions are met! 
            self.assertEqual('{"name": "John"}', schedule_job.job.kwargs)
        
