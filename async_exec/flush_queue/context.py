from async_exec.flush_queue.role import Queue
from async_exec.execute_jobs.context import ExecuteJob 

class FlushQueue(object):
    def __init__(self, queue):
        self.queue = Queue(queue)

    def __enter__(self):
        while True:
            next_job = self.queue.next_job()
            if next_job is None:
                break
            with ExecuteJob(next_job) as execute_job:
                pass
        return self

    def __exit__(self, type, value, traceback):
        Queue.revoke(self.queue)

