from async_exec.schedule_job.role import Task, full_name
from async_exec.tests.function_for_test import hello_world 
from datetime import datetime
from django.test import TestCase
from yas.stub import ModelStub

class TestScheduleJob(TestCase):
    def setUp(self):
        self.task = Task(ModelStub())
        
    def test_schedule_job_with_scheduled_time(self):
        # Arrange
        scheduled_time = datetime.now()
        # Ack
        self.task.schedule(scheduled_time) 
        # Assert
        self.assertEqual(scheduled_time, self.task.scheduled)

class TestSetFunction(TestCase):
    def setUp(self):
        self.task = Task(ModelStub())

    def test_set_call(self):
        #Ack
        self.task.set_call(hello_world)
        # Assert
        function_name = 'async_exec.tests.function_for_test.hello_world'
        self.assertEqual(function_name, self.task.name)
        
    def test_set_call_with_args(self):
        #Ack
        self.task.set_call(hello_world, 1, 2, 3)
        # Assert
        self.assertEqual("[1, 2, 3]", self.task.args)
        
    def test_set_call_with_args(self):
        #Ack
        self.task.set_call(hello_world, subject = 'Python rocks', tags = ['python', 'cool'])
        # Assert
        kwargs = '{"tags": ["python", "cool"], "subject": "Python rocks"}'
        self.assertEqual(kwargs, self.task.kwargs)

class TestFullName(TestCase):
    def test_full_name(self):
        # Ack
        fully_qualified_function_name = full_name(hello_world)
        # Assert
        self.assertEqual('async_exec.tests.function_for_test.hello_world', fully_qualified_function_name )

