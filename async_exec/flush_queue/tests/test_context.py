from async_exec.flush_queue.context import FlushQueue
from async_exec.models import Job
from datetime import datetime, timedelta
from django.test import TestCase
from yas.stub import ModelStub

class TestFlushEmptyQueue(TestCase):
    def test_no_next_job_left_after_flush_queue__empty_queue(self):
        queue = Job.objects
        with FlushQueue(queue) as context:
            self.assertIsNone(context.queue.next_job())

class TestFlushQueueWithJobsScheduledInPast(TestCase):
    def setUp(self):
        yesterday = datetime.now() - timedelta(days=1)
        function_name = 'async_exec.tests.function_for_test.hello_world'
        Job(name = function_name, scheduled = yesterday).save()
        Job(name = function_name, scheduled = yesterday).save()
        Job(name = function_name, scheduled = yesterday).save()

    def test_no_next_job_left_after_flushed_queue(self):
        queue = Job.objects
        with FlushQueue(queue) as context:
            self.assertIsNone(context.queue.next_job())

    def test_all_job_are_executed_after_flushed_queue(self):
        queue = Job.objects
        with FlushQueue(queue) as context:
            pass
        number_of_executed_jobs = Job.objects.filter(executed__isnull = False).count()
        self.assertEqual(3, number_of_executed_jobs)
        

class TestFlushQueueWithJobsScheduledInFuture(TestCase):
    def setUp(self):
        tomorrow = datetime.now() + timedelta(days=1)
        function_name = 'async_exec.tests.function_for_test.hello_world'
        Job(name = function_name, scheduled = tomorrow).save()
        Job(name = function_name, scheduled = tomorrow).save()
        Job(name = function_name, scheduled = tomorrow).save()

    def test_no_job_is_executed_after_flushed_queue(self):
        queue = Job.objects
        with FlushQueue(queue) as context:
            pass
        number_of_executed_jobs = Job.objects.filter(executed__isnull = False).count()
        self.assertEqual(0, number_of_executed_jobs)

    def test_no_next_job_after_flushed_queue(self):
        queue = Job.objects
        with FlushQueue(queue) as context:
            self.assertIsNone(context.queue.next_job())

