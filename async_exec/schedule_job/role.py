from datetime import datetime
from inspect import getmodule
from roles.django import ModelRoleType

def full_name(function):
    module_name = getmodule(function).__name__
    return '.'.join([module_name, function.func_name])

class Task(object):
    __metaclass__ = ModelRoleType

    def schedule(self, function_name, args=[], kwargs={}, time_to_execute = None):
        self.name = function_name
        self.args = args
        self.kwargs = kwargs
        self.scheduled = time_to_execute

