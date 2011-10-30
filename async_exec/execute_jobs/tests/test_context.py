from async_exec.execute_jobs.context import ExecuteJobs
from async_exec.models import Job
from datetime import datetime, timedelta
from django.test import TestCase
from yas.stub import ModelStub

class TestExecuteJobsWithEmptyQueue(TestCase):
    def test_no_next_job_left_after_execute_jobs__empty_queue(self):
        queue = Job.objects
        with ExecuteJobs(queue) as context:
            self.assertIsNone(context.priority_queue.find_first_job())

class TestExecuteJobsWithJobsScheduledInPast(TestCase):
    def setUp(self):
        yesterday = datetime.now() - timedelta(days=1)
        function_name = 'async_exec.tests.function_for_test.hello_world'
        Job(name = function_name, scheduled = yesterday).save()
        Job(name = function_name, scheduled = yesterday).save()
        Job(name = function_name, scheduled = yesterday).save()

    def test_no_next_job_left_after_flushed_queue(self):
        queue = Job.objects
        with ExecuteJobs(queue) as context:
            self.assertIsNone(context.priority_queue.find_first_job())

    def test_all_job_are_executed_after_flushed_queue(self):
        queue = Job.objects
        with ExecuteJobs(queue) as context:
            pass
        number_of_executed_jobs = Job.objects.filter(executed__isnull = False).count()
        self.assertEqual(3, number_of_executed_jobs)

    def test_executed_job_has_execution_time_logged(self):
        queue = Job.objects
        with ExecuteJobs(queue) as context:
            pass
        job = Job.objects.all()[0]
        self.assertIsNotNone(job.executed)


class TestExecuteJobsWithJobsScheduledInFuture(TestCase):
    def setUp(self):
        tomorrow = datetime.now() + timedelta(days=1)
        function_name = 'async_exec.tests.function_for_test.hello_world'
        Job(name = function_name, scheduled = tomorrow).save()
        Job(name = function_name, scheduled = tomorrow).save()
        Job(name = function_name, scheduled = tomorrow).save()

    def test_no_job_is_executed_after_flushed_queue(self):
        queue = Job.objects
        with ExecuteJobs(queue) as context:
            pass
        number_of_executed_jobs = Job.objects.filter(executed__isnull = False).count()
        self.assertEqual(0, number_of_executed_jobs)

    def test_no_next_job_after_flushed_queue(self):
        queue = Job.objects
        with ExecuteJobs(queue) as context:
            self.assertIsNone(context.priority_queue.find_first_job())

class TestExecuteJobsWithScheduledAndUnscheduledJobs(TestCase):
    def setUp(self):
        now = datetime.now()
        function_name = 'async_exec.tests.function_for_test.hello_world'
        Job(name = function_name, scheduled = now).save()
        Job(name = function_name).save()
        Job(name = function_name, scheduled = now).save()

    def test_unscheduled_jobs_are_executed_after_scheduled_jobs(self):
        """
        Scheduled jobs (job1 and job3) should be executed before unscheduled job (job2)
        """
        queue = Job.objects
        with ExecuteJobs(queue) as context:
            pass
        job1 = Job.objects.get(id=1)
        job2 = Job.objects.get(id=2)
        job3 = Job.objects.get(id=3)
        self.assertLess(job1.executed, job3.executed)
        self.assertLess(job3.executed, job2.executed)

