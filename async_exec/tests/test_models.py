from async_exec.models import Job 
from async_exec.tests.function_for_test import hello_world 
from datetime import datetime, timedelta
from django.test import TestCase

class TestJob(TestCase):
    def test_print_job_print_its_name(self):
        job_name = 'A Job'
        job = Job(name=job_name) 
        self.assertEqual(job_name, job.__unicode__())


class TestNextJob(TestCase):
    def test_next_job_is_none_for_empty_queue(self):
        next_job = Job.next_job()
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
        next_job = Job.next_job()
        self.assertEqual(job3, next_job) 

    def test_next_job_return_none_if_there_only_jobs_in_future(self):
        tomorrow = datetime.now() + timedelta(days=1)
        Job(scheduled = tomorrow).save()
        next_job = Job.next_job()
        self.assertIsNone(next_job)
        
