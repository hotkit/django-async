from async_exec.models import Job
from async_exec.schedule_job.context import ScheduleJob

def schedule(function, args = None, kwargs = None, schedule_time = None):
    job = Job()
    args = args or []
    kwargs = kwargs or {}
    with ScheduleJob(schedule_time, job, function, args = args, kwargs = kwargs) as context:
        # Conditions may not change in here because post conditions are met! 
        pass
    return job
    
