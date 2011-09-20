from async_exec.execute_job.context import ExecuteJob
from async_exec.models import Job
from datetime import datetime
from django.test import TestCase

class TestExecuteJob(TestCase):
    def setUp(self):
        self.job = Job()

    def test_execute_job_marks_job_as_executed(self):
        with ExecuteJob(self.job) as context:
            self.assertTrue(context.job.is_executed())
        
    def test_execute_job_logs_execution_time(self):
        before_execute = datetime.now()
        with ExecuteJob(self.job) as context:
            pass
        # check execution time in the database
        job = Job.objects.get(id = self.job.id) 
        self.assertIsNotNone(job.executed)
