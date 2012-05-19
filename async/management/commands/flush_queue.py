"""
    Django Async management commands.
"""
from datetime import datetime
from django.core.management.base import BaseCommand
from optparse import make_option

from async.models import Job


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

    def handle(self, **options):
        """Command implementation.
        """
        jobs = Job.objects.filter(executed=None).exclude(
            scheduled__gt=datetime.now())
        for job in jobs.iterator():
            print job
            job()
