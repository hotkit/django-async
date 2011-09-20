from async_exec.execute_job.role import Process
from datetime import datetime
from django.test import TestCase
from yas.stub import ModelStub

class TestProcess(TestCase):
    def test_is_execute_is_true_if_executed_time_is_set(self):
        process = Process(ModelStub())
        process.executed = datetime.now()
        self.assertTrue(process.is_executed())
        
    def test_is_execute_is_false_if_executed_time_is_not_set(self):
        process = Process(ModelStub())
        process.executed = None
        self.assertFalse(process.is_executed())

    def test_execute_set_execution_time(self):
        process = Process(ModelStub())
        process.execute() 
        self.assertIsNotNone(process.executed)

