from datetime import datetime
from roles import RoleType

class Queue(object):
    __metaclass__ = RoleType

    def next_job(self):
        now = datetime.now()
        remaining_job = self.filter(executed__isnull = True, scheduled__lt=now)
        return None if not remaining_job else remaining_job[0] 

