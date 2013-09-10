"""
    Django Async management commands.
"""
from datetime import datetime
from django.core.management.base import BaseCommand
from optparse import make_option
from lockfile import FileLock, AlreadyLocked

from async.models import Job


def acquire_lock(lockname):
    """Return a decorator for the given lock name
    """
    def decorator(handler):
        """Decorator for lock acquisition
        """
        def handle(self, **options):
            """Acquire the lock before running the method.
            """
            lock = FileLock(lockname)
            try:
                lock.acquire(timeout = -1)
            except AlreadyLocked:
                print 'Lock is already set, aborting.'
                return
            try:
                handler(self, **options)
            finally:
                lock.release()
        return handle
    return decorator


class Command(BaseCommand):
    """
        Invoke using:
            python manage.py flush_queue
    """
    option_list = BaseCommand.option_list + (
        make_option('--jobs', '-j', dest='jobs',
            help='The maximum number of jobs to run'),
    )
    help = 'Does a single pass over the asynchronous queue'

    @acquire_lock('async_flush_queue')
    def handle(self, **options):
        """Command implementation.

        This implementation is pretty ugly, but does behave in the
        right way.
        """
        while True:
            now = datetime.now()
            by_priority = (Job.objects
                .filter(executed=None)
                .exclude(scheduled__gt=now)
                .order_by('-priority'))
            number = by_priority.count()
            if number == 0:
                print "No jobs found for execution"
                return
            def run(jobs):
                """Run the jobs handed to it
                """
                for job in jobs.iterator():
                    print "%s: %s" % (job.id, unicode(job))
                    job.execute()
                    return False
                return True
            priority = by_priority[0].priority
            if run(Job.objects
                    .filter(executed=None, scheduled__lte=now,
                        priority=priority)
                    .order_by('scheduled', 'id')):
                run(Job.objects
                    .filter(executed=None, scheduled=None, priority=priority)
                    .order_by('id'))

