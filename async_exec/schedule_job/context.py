from async_exec.schedule_job.role import Task 

class ScheduleJob(object):
    def __init__(self, job_owner, job, function, time_to_execute = None):
        self.job_owner = job_owner
        self.job = job
        self.function = function
        self.time_to_execute = time_to_execute

    def __enter__(self):
        # pre conditions here
        self.job = Task(self.job)
        self.job.schedule(self.function, time_to_execute = self.time_to_execute)
        self.job.save() 
        return self

    def __exit__(self, type, value, traceback):
        Task(self.job)

