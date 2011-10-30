from async_exec.execute_jobs.role import Queue
from async_exec.models import Job 
from datetime import datetime, timedelta
from django.test import TestCase
from yas.stub import Stub

class TestNextJob(TestCase):
    def setUp(self):
        self.queue = Queue(Job.objects)

    def test_next_job_is_none_for_empty_queue(self):
        next_job = self.queue.next_job()
        self.assertIsNone(next_job)

    def test_next_job_return_first_unexecuted_job(self):
        """
        Scenario: there are 4 jobs, the first 2 have been executed, the last 2 have not
        Expect: job3 as it is first that has not been executed 
        """
        now = datetime.now()
        job1 = Job(name = '1', scheduled = now, executed = now)
        job1.save() 
        job2 = Job(name = '2', scheduled = now, executed = now)
        job2.save() 
        job3 = Job(name = '3', scheduled = now)
        job3.save() 
        job4 = Job(name = '4', scheduled = now)
        job4.save() 
        next_job = self.queue.next_job()
        self.assertEqual(job3, next_job) 

    def test_next_job_return_none_if_there_only_jobs_in_future(self):
        tomorrow = datetime.now() + timedelta(days=1)
        Job(scheduled = tomorrow).save()
        next_job = self.queue.next_job()
        self.assertIsNone(next_job)

