from django.test import TestCase
from async_exec.models import Job 


class TestModels(TestCase):
    def test_print_job_print_its_name(self):
        job_name = 'A Job'
        job = Job(name=job_name) 
        self.assertEqual(job_name, job.__unicode__())

    def test_create_job(self):
        def hello_world():
            print 'hello world'
        job = Job.create(hello_world)
        self.assertEqual(job.name, 'hello_world')
