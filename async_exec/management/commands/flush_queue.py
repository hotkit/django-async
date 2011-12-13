from optparse import make_option
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--jobs', '-j', dest='jobs',
            help='The maximum number of jobs to run'),
    )
    help = 'Does a single pass over the asynchronous queue'

    def handle(self, **options):
        print "Flushing queue..."
