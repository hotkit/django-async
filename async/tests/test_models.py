"""
    Testing that models work properly.
"""
from django.test import TestCase, TransactionTestCase

from async import schedule
from async.models import Error, Job


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
        self.assertEqual(job.identity,
            '289dbff9c1bd746fc444a20d396986857a6e8f04')

    def test_identity(self):
        """Make sure that the identity we get is the same as in another
        test when given the same arguments.
        """
        job = schedule('async.tests.test_models._fn')
        self.assertEqual(job.identity,
            '289dbff9c1bd746fc444a20d396986857a6e8f04')

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
        job = schedule('async.tests.test_models._fn',
            kwargs=dict(k='v', x=None))
        self.assertEqual(unicode(job),
            "async.tests.test_models._fn(x=None, k='v')")
        self.assertEqual(job.identity,
            '60941ebcc096c0223ba1db02b3d256f19ba553a3')

    def test_unicode_with_args_and_kwargs(self):
        """Make sure unicode handling deals with kwargs properly.
        """
        job = schedule('async.tests.test_models._fn',
            args=['argument'], kwargs=dict(k='v', x=None))
        self.assertEqual(unicode(job),
            "async.tests.test_models._fn('argument', x=None, k='v')")
        self.assertEqual(job.identity,
            '2ce2bb7935439a6ab3f111882f359a06b36bf995')


class TestError(TestCase):
    """Test the Error model.
    """

    def test_unicode(self):
        """Make sure the that the Unicode form of the Error works.
        """
        job = schedule('async.tests.test_models._fn')
        error = Error.objects.create(job=job, exception="Exception text")
        self.assertTrue(
            unicode(error).endswith(u' : Exception text'), unicode(error))

