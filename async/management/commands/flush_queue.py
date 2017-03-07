"""
    Django Async management commands.
"""
from __future__ import print_function
import django
from django.core.management.base import BaseCommand
try:
    # No name 'timezone' in module 'django.utils'
    # pylint: disable=E0611
    from django.utils import timezone
except ImportError: # pragma: no cover
    from datetime import datetime as timezone
from lockfile import FileLock, AlreadyLocked
from async.models import Job

if django.VERSION < (1,8):
    from optparse import make_option


def acquire_lock(lockname):
    """Return a decorator for the given lock name
    """
    def decorator(handler):
        """Decorator for lock acquisition
        """
        def handle(*args):
            """Acquire the lock before running the method.
            """
            lock = FileLock(lockname)
            try:
                lock.acquire(timeout=-1)
            except AlreadyLocked: # pragma: no cover
                print('Lock is already set, aborting.')
                return
            try:
                handler(*args)
            finally:
                lock.release()
        return handle
    return decorator


def run_queue(which, outof, limit, name_filter):
    """
        Code that actually executes the jobs in the queue.

        This implementation is pretty ugly, but does behave in the
        right way.
    """
    while limit:
        now = timezone.now()
        def run(limit, jobs):
            """Run the jobs handed to it
            """
            executed = 0
            for job in jobs.iterator():
                if job.id % outof == which % outof:
                    if (job.group and job.group.final and
                            job.group.final.pk == job.pk):
                        if not job.group.has_completed(job):
                            continue
                    print ("%s: %s" % (job.id, job))
                    job.execute()
                    executed = executed + 1
                    if executed >= limit:
                        break
            return executed
        by_priority = by_priority_filter = (Job.objects
            .filter(executed=None, cancelled=None,
                name__startswith=name_filter)
            .exclude(scheduled__gt=now)
            .order_by('-priority'))
        while limit:
            try:
                priority = by_priority[0].priority
            except IndexError:
                print("No jobs to execute")
                return
            executed = 1
            while executed and limit:
                executed = run(limit, Job.objects
                    .filter(executed=None, cancelled=None,
                        scheduled__lte=now, priority=priority,
                        name__startswith=name_filter)
                    .order_by('scheduled', 'id'))
                limit = limit - executed
            executed = 1
            while executed and limit:
                executed = run(limit, Job.objects
                    .filter(executed=None, cancelled=None,
                        scheduled=None, priority=priority,
                        name__startswith=name_filter)
                    .order_by('id'))
                limit = limit - executed
            by_priority = by_priority_filter.filter(
                priority__lt=priority)


class Command(BaseCommand):
    """
        Invoke using:
            python manage.py flush_queue
    """
    help = 'Does a single pass over the asynchronous queue'

    if django.VERSION < (1,8):
        option_list = BaseCommand.option_list + (
            make_option('--jobs', '-j', dest='jobs',
                        help='The maximum number of jobs to run'),
            make_option('--which', '-w', dest='which',
                        help='The worker ID number'),
            make_option('--outof', '-o', dest='outof',
                        help='How many workers there are'),
            make_option('--filter', '-f', dest='filter',
                        help='Filter jobs by fully qualified name'),
        )

    def add_arguments(self, parser):
        parser.add_argument('--jobs', '-j', dest='jobs',
                            help='The maximum number of jobs to run')
        parser.add_argument('--which', '-w', dest='which',
                            help='The worker ID number')
        parser.add_argument('--outof', '-o', dest='outof',
                            help='How many workers there are')
        parser.add_argument('--filter', '-f', dest='filter',
                            help='Filter jobs by fully qualified name')


    def handle(self, **options):
        """
            Command implementation.
        """
        jobs_limit = int(options.get('jobs') or 300)
        which = int(options.get('which') or 0)
        outof = int(options.get('outof') or 1)
        name_filter = str(options.get('filter') or '')

        acquire_lock('async_flush_queue%s' % which)(
            run_queue)(which, outof, jobs_limit, name_filter)
