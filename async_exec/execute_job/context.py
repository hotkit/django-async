from async_exec.execute_job.role import Process 
from datetime import datetime

class ExecuteJob(object):
    def __init__(self, job):
       self.job = Process(job)

    def __enter__(self):
        self.job.execute()
        self.job.save()
        return self 

    def __exit__(self, type, value, traceback):
        Process.revoke(self.job) 

