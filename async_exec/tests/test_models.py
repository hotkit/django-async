from django.test import TestCase
from async_exec.models import Job 


class TestModels(TestCase):
    def test_print_job_print_its_name(self):
        job_name = 'A Job'
        job = Job(name=job_name) 
        self.assertEqual(job_name, job.__unicode__())

