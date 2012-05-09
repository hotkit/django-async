from datetime import datetime
from importlib import import_module
from json import loads
from roles import RoleType
from roles.django import ModelRoleType

def load_function(full_name):
    items = full_name.split('.')
    # load 1st item as module to start with
    module = load_module(items[0])
    items[0] = module

    def keep_getting_attribute_of_next_element(module, component):
        try:
            import_module(module.__name__ + '.' + component)
        except ImportError, e:
            msg = 'No module named %s' % component
            if e.message == msg:
                pass
            else:
                raise e

        return getattr(module, component)

    return reduce(keep_getting_attribute_of_next_element, items)

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


class PriorityQueue(object):
    __metaclass__ = RoleType

    def find_first_job(self):
        now = datetime.now()
        remaining_job = self.filter(executed__isnull = True, scheduled__lt=now)
        return None if not remaining_job else remaining_job[0] 

class EconomyQueue(object):
    __metaclass__ = RoleType

    def find_first_job(self):
        remaining_job = self.filter(executed__isnull = True, scheduled__isnull=True)
        return None if not remaining_job else remaining_job[0] 

