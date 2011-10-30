from async_exec.execute_jobs.role import Process, PriorityQueue

class ExecuteJobs(object):
    def __init__(self, queue):
        self.priority_queue = PriorityQueue(queue)

    def __enter__(self):
        while True:
            next_job = self.priority_queue.find_first_job()
            if next_job is None:
                break
            Process(next_job)
            next_job.execute()
            next_job.save()
            Process.revoke(next_job) 
        return self

    def __exit__(self, type, value, traceback):
        PriorityQueue.revoke(self.priority_queue)

