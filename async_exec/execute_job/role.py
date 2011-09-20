from datetime import datetime
from roles.django import ModelRoleType

def load_function(full_name):
    module_name, function_name = split(full_name)
    module = __import__(module_name)
    function = getattr(module, function_name)
    return function 

def split(full_name):
    """
    Parameter:
    full_name = fully qualified name of a function
    Return (module_name, function_name)
    """
    items = full_name.split('.')
    function_name = items[-1]
    module_name = '.'.join(items[0:-1])
    return module_name, function_name

class Process(object):
    __metaclass__ = ModelRoleType

    def is_executed(self):
        return self.executed is not None

    def execute(self):
        self.executed = datetime.now()
