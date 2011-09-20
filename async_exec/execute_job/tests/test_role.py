from async_exec.execute_job.role import Process, load_function, split
from async_exec.tests.function_for_test import hello_world
from datetime import datetime
from django.test import TestCase
from yas.stub import ModelStub

class TestProcess(TestCase):
    def setUp(self):
        self.process = Process(ModelStub())
        
    def test_is_execute_is_true_if_executed_time_is_set(self):
        self.process.executed = datetime.now()
        self.assertTrue(self.process.is_executed())
        
    def test_is_execute_is_false_if_executed_time_is_not_set(self):
        self.process.executed = None
        self.assertFalse(self.process.is_executed())

    def test_execute_set_execution_time(self):
        self.process.execute() 
        self.assertIsNotNone(self.process.executed)

    def test_execute_really_call_function(self):
        pass


class TestLoadFunction(TestCase):
    def test_load_function(self):
        function_name = 'async_exec.tests.function_for_test.hello_world'
        function = load_function(function_name)
        self.assertEqual(hello_world, function)


class TestSplit(TestCase):
    def test_split(self):
        full_name = 'async_exec.tests.function_for_test.hello_world'
        module_name, function_name = split(full_name)
        self.assertEqual('async_exec.tests.function_for_test', module_name)
        self.assertEqual('hello_world', function_name)

