from async_exec.execute_jobs.role import Process, load_function, load_module
from async_exec.tests.function_for_test import hello_world
from datetime import datetime
from django.test import TestCase
from mock import patch
from yas.stub import ModelStub

import json

class TestProcess(TestCase):
    def setUp(self):
        self.process = Process(ModelStub())
        
    # test is_execute
    def test_is_execute_is_true_if_executed_time_is_set(self):
        self.process.executed = datetime.now()
        self.assertTrue(self.process.is_executed())
        
    def test_is_execute_is_false_if_executed_time_is_not_set(self):
        self.process.executed = None
        self.assertFalse(self.process.is_executed())

    # test_execute
    def test_execute_set_execution_time(self):
        self.process.name = 'async_exec.tests.function_for_test.hello_world'
        self.process.execute() 
        self.assertIsNotNone(self.process.executed)

    @patch('async_exec.tests.function_for_test.sample_function')
    def test_execute_really_call_function(self, mocked_sample_function):
        self.process.name = 'async_exec.tests.function_for_test.sample_function'
        self.process.execute() 
        self.assertTrue(mocked_sample_function.called)

    @patch('async_exec.tests.function_for_test.sample_function')
    def test_execute_pass_args_in(self, mocked_sample_function):
        self.process.name = 'async_exec.tests.function_for_test.sample_function'
        self.process.args = '["Python", "cool"]'
        self.process.kwargs = '{"DCI": "rocks"}'
        self.process.execute() 
        mocked_sample_function.assert_called_once_with('Python', 'cool', DCI='rocks')

    # test get_args
    def test_get_args__happy(self):
        self.process.args = '[1, 2, 3]'
        args = self.process.get_args()
        self.assertListEqual([1, 2, 3], args)

    def test_get_args_return_empty_array_when_args_is_none(self):
        self.process.args = None 
        args = self.process.get_args()
        self.assertListEqual([], args)

    def test_get_args_return_empty_array_when_args_is_empty_string(self):
        self.process.args = '' 
        args = self.process.get_args()
        self.assertListEqual([], args)

    # test get_kwargs
    def test_get_kwargs__happy(self):
        self.process.kwargs = '{"DCI": "rocks!"}'
        kwargs = self.process.get_kwargs()
        self.assertDictEqual({'DCI': 'rocks!'}, kwargs)

    def test_get_kwargs_return_empty_dict_when_kwargs_is_none(self):
        self.process.kwargs = None 
        kwargs = self.process.get_kwargs()
        self.assertDictEqual({}, kwargs)

    def test_get_args_return_empty_array_when_args_is_empty_string(self):
        self.process.kwargs = '' 
        kwargs = self.process.get_kwargs()
        self.assertDictEqual({}, kwargs)


class TestLoadFunction(TestCase):
    def test_load_function(self):
        function_name = 'async_exec.tests.function_for_test.hello_world'
        function = load_function(function_name)
        self.assertEqual(hello_world, function)

    def test_load_module(self):
        module_name = 'json'
        module = load_module(module_name)
        self.assertEqual(json, module)

