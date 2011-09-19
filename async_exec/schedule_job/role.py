from datetime import datetime
from roles.django import ModelRoleType

class Task(object):
    __metaclass__ = ModelRoleType

    def schedule(self, time_to_execute = None):
        time_to_execute = time_to_execute or datetime.now()
        self.scheduled = time_to_execute

