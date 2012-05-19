"""
    Testing that models work properly.
"""
from django.test import TestCase

from async import schedule
from async.models import Job


class TestJob(TestCase):
    """Make sure the basic model features work properly.
    """
    def test_model_creation(self):
        """Make sure schedule API works.
        """
        job = schedule('async.cron')
        self.assertEqual(Job.objects.all().count(), 1)
        self.assertEqual(unicode(job), "async.cron()")

    def test_unicode_with_args(self):
        """Make sure unicode handling deals with args properly.
        """
        self.assertEqual(unicode(schedule(
                'example.function', args=['argument'])),
            'example.function(argument)')
        self.assertEqual(unicode(schedule(
                'example.function', args=['a1', 'a2'])),
            'example.function(a1, a2)')
        self.assertEqual(unicode(schedule(
                'example.function.somewhere', args=[1, 2])),
            'example.function.somewhere(1, 2)')
        self.assertEqual(unicode(schedule(
                'example.function.somewhere', args=[dict(k='v', x=None)])),
            "example.function.somewhere({'x': None, 'k': 'v'})")

    def test_unicode_with_kwargs(self):
        """Make sure unicode handling deals with kwargs properly.
        """
        self.assertEqual(unicode(schedule(
                'example.function.somewhere', kwargs=dict(k='v', x=None))),
            "example.function.somewhere(x=None, k='v')")

    def test_unicode_with_args_and_kwargs(self):
        """Make sure unicode handling deals with kwargs properly.
        """
        self.assertEqual(unicode(schedule(
                'example.function.somewhere',
                    args=['argument'], kwargs=dict(k='v', x=None))),
            "example.function.somewhere(argument, x=None, k='v')")
