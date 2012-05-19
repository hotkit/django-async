"""
    Testing that models work properly.
"""
from django.test import TransactionTestCase

from async import schedule
from async.models import Job


def _fn(*_a, **_kw):
    """Test function.
    """
    pass


class TestJob(TransactionTestCase):
    """Make sure the basic model features work properly.
    """
    def test_model_creation(self):
        """Make sure schedule API works.
        """
        job = schedule('async.tests.test_models._fn')
        self.assertEqual(Job.objects.all().count(), 1)
        self.assertEqual(unicode(job), "async.tests.test_models._fn()")

    def test_unicode_with_args(self):
        """Make sure unicode handling deals with args properly.
        """
        self.assertEqual(unicode(schedule(
                'async.tests.test_models._fn', args=['argument'])),
            "async.tests.test_models._fn('argument')")
        self.assertEqual(unicode(schedule(
                'async.tests.test_models._fn', args=['a1', 'a2'])),
            "async.tests.test_models._fn('a1', 'a2')")
        self.assertEqual(unicode(schedule(
                'async.tests.test_models._fn', args=[1, 2])),
            'async.tests.test_models._fn(1, 2)')
        self.assertEqual(unicode(schedule(
                'async.tests.test_models._fn', args=[dict(k='v', x=None)])),
            "async.tests.test_models._fn({'x': None, 'k': 'v'})")

    def test_unicode_with_kwargs(self):
        """Make sure unicode handling deals with kwargs properly.
        """
        self.assertEqual(unicode(schedule(
                'async.tests.test_models._fn', kwargs=dict(k='v', x=None))),
            "async.tests.test_models._fn(x=None, k='v')")

    def test_unicode_with_args_and_kwargs(self):
        """Make sure unicode handling deals with kwargs properly.
        """
        self.assertEqual(unicode(schedule(
                'async.tests.test_models._fn',
                    args=['argument'], kwargs=dict(k='v', x=None))),
            "async.tests.test_models._fn('argument', x=None, k='v')")
