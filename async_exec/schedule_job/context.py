from async_exec.schedule_job.role import Task 

class ScheduleJob(object):
    def __init__(self, time_to_execute, job, function, *args, **kwargs):
        # pre conditions here
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.time_to_execute = time_to_execute
        # assign roles
        self.job = Task(job)

    def __enter__(self):
        self.job.set_call(self.function, *self.args, **self.kwargs)
        if self.time_to_execute:
            self.job.schedule(self.time_to_execute)
        self.job.save() 
        return self

    def __exit__(self, type, value, traceback):
        Task.revoke(self.job)

