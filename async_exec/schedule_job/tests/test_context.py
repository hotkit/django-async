from datetime import datetime
from django.test import TestCase
from async_exec.schedule_job.context import ScheduleJob
from async_exec.schedule_job.tests.function_for_test import sample_function
from async_exec.models import Job

class TestScheduleJob(TestCase):
    def test_successfully_schedule_job_with_no_scheduled_time(self):
        owner = 'An application' 
        job = Job.create(sample_function, name = 'John')
        with ScheduleJob(owner, job, sample_function) as schedule_job:
            # Conditions may not change in here because post conditions are met! 
            self.assertTrue(schedule_job.job)
            self.assertEqual(schedule_job.job.scheduled, None)

    def test_successfully_schedule_job_with_scheduled_time(self):
        owner = 'An application' 
        job = Job.create(sample_function, name = 'John')
        scheduled_time = datetime.now()
        with ScheduleJob(owner, job, sample_function, scheduled_time) as schedule_job:
            # Conditions may not change in here because post conditions are met! 
            self.assertTrue(schedule_job.job)
            self.assertEqual(schedule_job.job.scheduled, scheduled_time)
        
