from async_exec.execute_jobs.role import Process, PriorityQueue, EconomyQueue
from roles import clone

class ExecuteJobs(object):
    def __init__(self, queue):
        self.priority_queue = PriorityQueue(queue, method = clone)
        self.economy_queue = EconomyQueue(queue, method = clone)

    def __enter__(self):
        while process(self.priority_queue):
            pass
        while process(self.economy_queue): 
            pass
        return self

    def __exit__(self, type, value, traceback):
        PriorityQueue.revoke(self.priority_queue)
        EconomyQueue.revoke(self.economy_queue)

def process(queue):
    next_job = queue.find_first_job()
    if not next_job:
        return False
    with Process.played_by(next_job):
        next_job.execute()
    next_job.save()
    return True
