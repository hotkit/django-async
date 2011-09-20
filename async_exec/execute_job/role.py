from datetime import datetime
from json import loads
from roles.django import ModelRoleType

def load_function(full_name):
    items = full_name.split('.')
    # load 1st item as module to start with
    module = load_module(items[0])
    items[0] = module
    # keep getting attribute of next element
    attr_of = lambda module, component: getattr(module, component)
    return reduce(attr_of, items) 

def load_module(module_name):
    return __import__(module_name)

class Process(object):
    __metaclass__ = ModelRoleType

    def is_executed(self):
        return self.executed is not None

    def execute(self):
        function = self.get_function()
        args = self.get_args()
        kwargs = self.get_kwargs()
        function(*args, **kwargs)
        self.executed = datetime.now()

    def get_function(self):
        return load_function(self.name)

    def get_args(self):
        args = getattr(self, 'args', None)
        return [] if not args else loads(args)

    def get_kwargs(self):
        kwargs = getattr(self, 'kwargs', None)
        return {} if not kwargs else loads(kwargs)

