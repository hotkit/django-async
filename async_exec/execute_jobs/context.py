from async_exec.execute_jobs.role import Process, PriorityQueue, EconomyQueue
from roles import clone

class ExecuteJobs(object):
    def __init__(self, queue):
        self.priority_queue = PriorityQueue(queue, method = clone)
        self.economy_queue = EconomyQueue(queue, method = clone)

    def __enter__(self):
        while True:
            while True:
                next_job = self.priority_queue.find_first_job()
                if not next_job:
                    break
                Process(next_job)
                next_job.execute()
                next_job.save()
                Process.revoke(next_job) 
            next_job = self.economy_queue.find_first_job()
            if not next_job:
                break
            Process(next_job)
            next_job.execute()
            next_job.save()
            Process.revoke(next_job) 
        return self

    def __exit__(self, type, value, traceback):
        PriorityQueue.revoke(self.priority_queue)
        EconomyQueue.revoke(self.economy_queue)

