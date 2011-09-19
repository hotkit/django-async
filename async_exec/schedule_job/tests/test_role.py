from async_exec.schedule_job.role import Task, full_name
from async_exec.tests.function_for_test import hello_world 
from datetime import datetime
from django.test import TestCase
from yas.stub import Stub

class RoledStub(Stub):
    class Meta:
        proxy = False 

class TestTask(TestCase):
    def test_schedule_job_with_scheduled_time(self):
        # Arrange
        task = Task(RoledStub())
        scheduled_time = datetime.now()
        # Ack
        task.schedule('async_exec.tests.function_for_test.hello_world', time_to_execute = scheduled_time) 
        # Assert
        self.assertEqual(scheduled_time, task.scheduled)


class TestFullName(TestCase):
    def test_full_name(self):
        # Ack
        fully_qualified_function_name = full_name(hello_world)
        # Assert
        self.assertEqual('async_exec.tests.function_for_test.hello_world', fully_qualified_function_name )

