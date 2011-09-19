from datetime import datetime
from inspect import getmodule
from json import dumps
from roles.django import ModelRoleType

def full_name(function):
    module_name = getmodule(function).__name__
    return '.'.join([module_name, function.func_name])

class Task(object):
    __metaclass__ = ModelRoleType

    def set_call(self, function, *args, **kwargs):
        self.name = full_name(function)
        self.args = dumps(args)
        self.kwargs = dumps(kwargs)

    def schedule(self, time_to_execute):
        self.scheduled = time_to_execute

