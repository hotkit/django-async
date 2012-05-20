"""
    Django manage.py command to show the queue health
"""
from django.core.management.base import BaseCommand
from simplejson import dumps

from async.api import health


class Command(BaseCommand):
    """
        Invoke using:
            python manage.py queue_health
    """
    help = 'Prints information about the queue in JSON format.'

    def handle(self, **options):
        """Command implementation.
        """
        print dumps(health())

