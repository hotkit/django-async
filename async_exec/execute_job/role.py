from datetime import datetime
from roles.django import ModelRoleType

class Process(object):
    __metaclass__ = ModelRoleType

    def is_executed(self):
        return self.executed is not None

    def execute(self):
        self.executed = datetime.now()
