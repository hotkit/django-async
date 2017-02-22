"""
    Django manage.py command to show the queue health
"""
from __future__ import print_function
from django.core.management.base import BaseCommand, CommandError
from simplejson import dumps

from async.api import health
from async.stats import estimate_queue_completion, \
    estimate_rough_queue_completion


class Command(BaseCommand):
    """
        Invoke using:
            python manage.py queue_health

        arguments: rough - (default) Gets rough estimate of queue completion
                   precise - Gets a more precise estimate of queue completion
    """

    help = 'Prints information about the queue in JSON format.'

    def add_arguments(self, parser):
        parser.add_argument('--algorithm', '-a', dest='algorithm',
                    help="""The algorithm for queue estimation.
                    Options: rough(default), precise""")

    def handle(self, *args, **options):
        """Command implementation.
        """
        algorithm = options.get('algorithm' or None)
        if algorithm == "rough":
            estimation_fn = estimate_rough_queue_completion
        elif algorithm == "precise" or algorithm is None:
            estimation_fn = estimate_queue_completion
        else:
            raise CommandError("Unknown option for estimation algorithm")
        print(dumps(health(estimation_fn)))
