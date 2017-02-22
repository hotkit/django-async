"""
    Testing that models work properly.
"""
import datetime
import unittest

try:
    from django.test import TestCaseTransactionTestCase
except ImportError:
    from django.test import TestCase
    TransactionTestCase = TestCase
from django.core.exceptions import ValidationError
try:
    # No name 'timezone' in module 'django.utils'
    # pylint: disable=E0611
    from django.utils import timezone
except ImportError:
    from datetime import datetime as timezone

from async import schedule
from async.models import Error, Job, Group


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
        try:
            self.assertEqual(unicode(job), "async.tests.test_models._fn()")
        except NameError:
            self.assertEqual(str(job), "async.tests.test_models._fn()")
        self.assertEqual(job.identity,
            '289dbff9c1bd746fc444a20d396986857a6e8f04')

    def test_model_creation_with_no_group(self):
        """Make sure schedule API works with no group.
        """
        job = schedule('async.tests.test_models._fn')
        self.assertEqual(Job.objects.all().count(), 1)
        self.assertEqual(job.group, None)

    def test_model_creattion_with_group(self):
        """make sure schedule API works with group.
        """
        group = Group.objects.create(
            reference='test-group',
            description='for testing')
        job = schedule('async.tests.test_models._fn')
        job.group = group
        job.save()

        self.assertEqual(Job.objects.all().count(), 1)
        self.assertEqual(job.group, group)

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
        ## ToDo: Fix this later
        try:
            self.assertEqual(unicode(schedule(
                    'async.tests.test_models._fn', args=['argument'])),
                "async.tests.test_models._fn('argument')")
            self.assertEqual(unicode(schedule(
                    'async.tests.test_models._fn', args=['a1', 'a2'])),
                "async.tests.test_models._fn('a1', 'a2')")
            self.assertEqual(unicode(schedule(
                    'async.tests.test_models._fn', args=[1, 2])),
                'async.tests.test_models._fn(1, 2)')
        except NameError:
            self.assertEqual(str(schedule(
                'async.tests.test_models._fn', args=['argument'])),
                "async.tests.test_models._fn('argument')")
            self.assertEqual(str(schedule(
                'async.tests.test_models._fn', args=['a1', 'a2'])),
                "async.tests.test_models._fn('a1', 'a2')")
            self.assertEqual(str(schedule(
                'async.tests.test_models._fn', args=[1, 2])),
                'async.tests.test_models._fn(1, 2)')

    def test_unicode_with_kwargs(self):
        """Make sure unicode handling deals with kwargs properly.
        """
        job = schedule('async.tests.test_models._fn',
            kwargs=dict(k='v', x=None))
        try:
            self.assertEqual(unicode(job),
            "async.tests.test_models._fn(k='v', x=None)")
        except NameError:
            self.assertEqual(str(job),
            "async.tests.test_models._fn(k='v', x=None)")
        self.assertEqual(job.identity,
            '236a244a0cd845bb5a427db495ec830fa4ab9d93')

    def test_unicode_with_args_and_kwargs(self):
        """Make sure unicode handling deals with kwargs properly.
        """
        job = schedule('async.tests.test_models._fn',
            args=['argument'], kwargs=dict(k='v', x=None))
        try:
            self.assertEqual(unicode(job),
            "async.tests.test_models._fn('argument', k='v', x=None)")
        except:
            self.assertEqual(str(job),
            "async.tests.test_models._fn('argument', k='v', x=None)")
        self.assertEqual(job.identity,
            '9abc86055107d5b5aa97ea32e098580543680c27')


class TestError(TestCase):
    """Test the Error model.
    """

    def test_unicode(self):
        """Make sure the that the Unicode form of the Error works.
        """
        job = schedule('async.tests.test_models._fn')
        error = Error.objects.create(job=job, exception="Exception text")
        try:
            self.assertTrue(unicode(error).endswith(u' : Exception text'), unicode(error))
        except NameError:
            self.assertTrue(str(error).endswith(' : Exception text'), str(error))


class TestGroup(TestCase):
    """Test the Group model.
    """
    def setUp(self):
        self.g1 = Group.objects.create(
                reference='group1',
                description='test group1'
            )
        self.j1 = Job.objects.create(
                name='job1',
                args='[]',
                kwargs='{}',
                meta='{}',
                priority=3,
            )

        self.j2 = Job.objects.create(
                name='job2',
                args='[]',
                kwargs='{}',
                meta='{}',
                priority=3,
            )

        self.j3 = Job.objects.create(
                name='job3',
                args='[]',
                kwargs='{}',
                meta='{}',
                priority=3,
            )

    def test_model_creation(self):
        """ Test if can create model. Get new instance.
        """
        group = Group.objects.create(
            reference='test-group',
            description='for testing'
        )

        self.assertTrue(Group.objects.all().count(), 1)
        try:
            self.assertEqual(unicode(group), u'test-group')
        except NameError:
            self.assertEqual(str(group), 'test-group')
        self.assertEqual(group.description, 'for testing')

    def test_creating_group_with_duplicate_reference_and_executed_job(self):
        """ Create new group with reference same as old group which has
            one job and already executed. Creating should success.
        """
        self.j1.group = self.g1
        self.j1.save()
        self.j2.group = self.g1
        self.j2.save()

        self.j1.executed = timezone.now()
        self.j1.save()
        self.j2.cancelled = timezone.now()
        self.j2.save()

        g2 = Group.objects.create(reference=self.g1.reference)
        self.assertEqual(
            Group.objects.filter(reference=self.g1.reference).count(), 2)

    def test_cancelled_jobs_allow_new_group(self):
        """ Make sure that a cancelled job allows us to make a new
            group with the same reference.
        """
        self.j1.group = self.g1
        self.j1.cancelled = timezone.now()
        self.j1.save()

        g2 = Group.objects.create(reference=self.g1.reference)
        self.assertEqual(
            Group.objects.filter(reference=self.g1.reference).count(), 2)

    def test_creating_group_with_duplicate_reference_and_has_one_unexecuted_job(self):
        """ Create new group with reference same as old group which has
            unexecuted job. Creating should not success.
        """

        # Assiging j1, j2, j3 to group1
        self.j1.group = self.g1
        self.j1.save()
        self.j2.group = self.g1
        self.j2.save()
        self.j3.group = self.g1
        self.j3.save()

        # Mark executed for j1, j2
        self.j1.executed = timezone.now()
        self.j1.save()
        self.j2.executed = timezone.now()
        self.j2.save()

        with self.assertRaises(ValidationError) as e:
            Group.objects.create(reference=self.g1.reference)
        self.assertTrue(isinstance(e.exception, ValidationError))
        self.assertEqual(Group.objects.filter(reference=self.g1.reference).count(), 1)

    def test_adding_job_to_group_that_has_executed_job(self):
        """ Add job to group which have one executed job.
        """
        self.j1.group = self.g1
        self.j1.executed = timezone.now()
        self.j1.save()

        with self.assertRaises(ValidationError) as e:
            self.j2.group = self.g1
            self.j2.save()
        self.assertTrue(isinstance(e.exception, ValidationError))
        self.assertEqual(Job.objects.filter(group=self.g1).count(), 1)

    def test_adding_job_to_group_that_has_cancelled_job(self):
        """ Add job to group which have one cancelled job.
        """
        self.j1.group = self.g1
        self.j1.cancelled = timezone.now()
        self.j1.save()

        with self.assertRaises(ValidationError) as e:
            self.j2.group = self.g1
            self.j2.save()
        self.assertTrue(isinstance(e.exception, ValidationError))
        self.assertEqual(Job.objects.filter(group=self.g1).count(), 1)

    def test_adding_job_to_group_that_has_unexecuted_job(self):
        """ Add jobs to group which has unexecuted job.
        """
        self.j1.group = self.g1
        self.j1.save()
        self.j2.group = self.g1
        self.j2.save()

        self.assertEqual(Group.objects.get(reference=self.g1.reference).jobs.count(), 2)

    def test_adding_job_to_executed_group(self):
        """ Adding a new job to a fully executed group creates a new group.
        """
        self.j1.group = self.g1
        self.j1.executed = timezone.now()
        self.j1.save()

        job = schedule('async.tests.test_models._fn',
            group=self.g1.reference)
        self.assertEqual(job.group.reference, self.g1.reference)
        self.assertNotEqual(job.group.pk, self.g1.pk)

    def test_schedule_passing_group_instance(self):
        """ Scheduling a job passing in a group object works.
        """
        job = schedule('async.tests.test_models._fn',
            group=self.g1)
        self.assertEqual(job.group.pk, self.g1.pk)

