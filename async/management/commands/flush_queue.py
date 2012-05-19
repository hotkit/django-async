"""
    Django Async management commands.
"""
from optparse import make_option
from django.core.management.base import BaseCommand


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
            scheduled_gt=datetime.now())
        for job in jobs.iterator():
            print job
            job()
