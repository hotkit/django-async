from django.test import TestCase
from async_exec.schedule_job.context import ScheduleJob
from async_exec.schedule_job.tests.function_for_test import sample_function
from async_exec.models import Job

class TestScheduleJob(TestCase):
    def test_successfully_schedule_job(self):
        owner = 'An application' 
        job = Job.create(sample_function, name = 'John')
        with ScheduleJob(owner, job) as schedule_job:
            # Conditions may not change in here because post conditions are met! 
            self.assertTrue(schedule_job.job)

