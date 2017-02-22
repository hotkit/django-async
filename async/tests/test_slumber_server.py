"""
    Tests for the Slumber operations.
"""
from datetime import timedelta
from simplejson import dumps, loads
from mock import patch
import unittest

import django
from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.core.exceptions import ValidationError
try:
    # No name 'timezone' in module 'django.utils'
    # pylint: disable=E0611
    from django.utils import timezone
except ImportError:
    from datetime import datetime as timezone

from async.models import Job, Group, Error

NoSlumber = False
try:
    from slumber import data_link
    from async.slumber_operations import Progress
except ImportError:
    NoSlumber = True

# Instance of 'WSGIRequest' has no 'status_code' member
#  (but some types could not be inferred)
# pylint: disable=E1103


@unittest.skipIf(NoSlumber, True)
class TestSlumber(TestCase):
    """Make sure that Slumber is wired in properly.
    """
    maxDiff = None

    def test_slumber_root(self):
        """Make sure Slumber is properly wired in.
        """
        response = self.client.get('/slumber/')
        self.assertEqual(response.status_code, 200)
        json = loads(response.content)
        self.assertIsNone(json['services'], dumps(json, indent=2))

@unittest.skipIf(NoSlumber, True)
class WithUser(object):
    def setUp(self):
        super(WithUser, self).setUp()
        self.user = User(username='test', is_active=True, is_staff=True)
        self.user.set_password('password')
        self.user.save()
        self.client.login(username='test', password='password')
        self.permission = Permission.objects.get(codename='add_job')
        self.user.user_permissions.add(self.permission)

@unittest.skipIf(NoSlumber, True)
class TestSchedule(WithUser, TestCase):
    """Make sure the schedule API wrapper works.
    """
    URL = '/slumber/async/Job/schedule/'

    def test_get_works(self):
        """Make sure the operation is wired in. Don't expect any output yet.
        """
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 200)
        json = loads(response.content)
        self.assertEqual(json, dict(
            _meta={'message': 'OK', 'status': 200, 'username': 'test'}))

    def test_simple_post_works(self):
        """Make sure the basic post functionality works.
        """
        response = self.client.post(self.URL, dict(
            name='test-job-1'))
        self.assertEqual(response.status_code, 200)
        job = Job.objects.get(name='test-job-1')
        self.assertEqual(job.args, '[]')
        self.assertIsNone(job.scheduled)
        json = loads(response.content)
        self.assertEqual(json, dict(
            job=dict(id=job.id),
            _meta={'message': 'OK', 'status': 200, 'username': 'test'}))

    def test_args_multipart_content(self):
        """Make sure that arguments are properly processed when using a
        normal POST.
        """
        response = self.client.post(self.URL, dict(
            name='test-job-1', args=[1, True, "Hello"]))
        self.assertEqual(response.status_code, 200)
        job = Job.objects.get(name='test-job-1')
        self.assertEqual(job.args, dumps(["1", "True", "Hello"]))
        self.assertIsNone(job.scheduled)
        json = loads(response.content)
        self.assertEqual(json, dict(
            job=dict(id=job.id),
            _meta={'message': 'OK', 'status': 200, 'username': 'test'}))

    def test_args_json(self):
        """Make sure that arguments are properly processed when using a
        normal POST.
        """
        response = self.client.post(self.URL, dumps(dict(
                name='test-job-1', args=[1, True, "Hello"])),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        job = Job.objects.get(name='test-job-1')
        self.assertEqual(job.args, dumps([1, True, "Hello"]))
        self.assertIsNone(job.scheduled)
        json = loads(response.content)
        self.assertEqual(json, dict(
            job=dict(id=job.id),
            _meta={'message': 'OK', 'status': 200, 'username': 'test'}))

    def test_run_at(self):
        """Make sure that the run at time is properly handled.
        """
        scheduled = timezone.now() + timedelta(days=1)
        response = self.client.post(self.URL, dict(
            name='test-job-1', run_after=scheduled))
        self.assertEqual(response.status_code, 200)
        job = Job.objects.get(name='test-job-1')
        self.assertEqual(job.args, '[]')
        self.assertEqual(job.scheduled, scheduled)
        json = loads(response.content)
        self.assertEqual(json, dict(
            job=dict(id=job.id),
            _meta={'message': 'OK', 'status': 200, 'username': 'test'}))

    def test_create_job_with_group(self):
        """Create job with group reference.
        """
        scheduled = timezone.now() + timedelta(days=1)
        group = Group.objects.create(
                reference='test-group-1',
                description='info')
        response = self.client.post(self.URL, dict(
                name='test-job-1',
                run_after=scheduled,
                group=group.reference))
        self.assertEqual(response.status_code, 200)
        job = Job.objects.get(name='test-job-1')
        self.assertEqual(job.group.reference, group.reference)

    def test_create_job_with_non_exist_group(self):
        """Create job with non exist group creates one
        """
        scheduled = timezone.now() + timedelta(days=1)
        response = self.client.post(self.URL, dict(
                name='test-job-1',
                run_after=scheduled,
                group='non-exist-group'))
        self.assertEqual(response.status_code, 200)
        json = loads(response.content)
        self.assertEqual(json['_meta'], {
            'status': 200,
            'username': 'test',
            'message': 'OK'})
        job = Job.objects.get(pk=json['job']['id'])
        self.assertEqual(job.group.reference, 'non-exist-group')
        self.assertEqual(
            Group.objects.filter(reference='non-exist-group').count(), 1)

    def test_create_job_with_multiple_group_same_reference(self):
        """Create job by assiging multiple group
        current job should has been assign by latest group
        """
        scheduled = timezone.now() + timedelta(days=1)
        g1 = Group.objects.create(reference='multiple-group')
        g2 = Group.objects.create(reference='multiple-group')
        g3 = Group.objects.create(reference='multiple-group')
        response = self.client.post(self.URL, dict(
            name='test-job-1',
            run_after=scheduled,
            group='multiple-group'))
        self.assertEqual(response.status_code, 200)
        j1 = Job.objects.get(name='test-job-1')
        self.assertEqual(Group.objects.filter(
            reference='multiple-group').count(), 3
        )
        self.assertEqual(j1.group.reference, g3.reference)
        self.assertNotEqual(j1.group.created, g1.created)
        self.assertNotEqual(j1.group.created, g2.created)
        self.assertEqual(j1.group.created, g3.created)

    def test_create_job_with_group_which_has_executed_job(self):
        """Create job by assigning group which already has executed job.
        So it should get ValidationError.
        """
        scheduled = timezone.now() + timedelta(days=1)
        g1 = Group.objects.create(reference='test-group')

        j1 = Job.objects.create(
            name='test-job-1', group=g1,
            args='[]', kwargs='{}', meta='{}', priority=5)
        j2 = Job.objects.create(
            name='test-job-2', group=g1,
            args='[]', kwargs='{}', meta='{}', priority=5)
        j1.executed = timezone.now() - timedelta(days=30)
        j1.save()
        with self.assertRaises(ValidationError) as e:
            response = self.client.post(self.URL, dict(
                name='test-job-3',
                run_after=scheduled,
                group='test-group'))

    def test_group_progres_url(self):
        """Make sure that references with odd characters still generate
        correct progress URLs.
        """
        g1 = Group.objects.create(reference="space test")
        response = self.client.get('/slumber/async/Group/data/%s/' % g1.pk)
        self.assertEqual(response.status_code, 200)
        json = loads(response.content)
        self.assertEqual(json['operations']['progress'],
            '/slumber/async/Group/progress/space%20test/')

@unittest.skipIf(NoSlumber, True)
class TestProgress(WithUser, TestCase):
    URL = '/slumber/async/Group/progress/'

    @unittest.skipIf(django.VERSION[:2], (1, 0))
    def test_get_work(self):
        """Test normal get request work.
        """
        group_name = 'test-ddrun'
        group1 = Group.objects.create(reference=group_name)
        Job.objects.create(
            name='test-job1',
            args='[]',
            kwargs='{}',
            meta='{}',
            priority=3,
            group=group1
        )
        Job.objects.create(
            name='test-job2',
            args='[]',
            kwargs='{}',
            meta='{}',
            priority=3,
            group=group1
        )
        test_url = self.URL + group_name + '/'

        response = self.client.get(test_url)
        self.assertEqual(response.status_code, 200)

        json = loads(response.content)
        self.assertEqual(json['_meta'],
            {'message': 'OK', 'status': 200, 'username': 'test'}
        )

        json_progress = json.get('progress')
        self.assertTrue(json_progress)
        self.assertEqual(json_progress.get('id'), group1.id)
        self.assertEqual(json_progress.get('created'), group1.created.isoformat())
        self.assertIsNone(json_progress.get('last_job_completed'))
        self.assertEqual(json_progress.get('total_jobs'), group1.jobs.count())
        self.assertEqual(json_progress.get('total_executed_jobs'), 0)
        self.assertEqual(json_progress.get('total_unexecuted_jobs'), 2)
        self.assertEqual(json_progress.get('total_error_jobs'), 0)
        self.assertIsNone(json_progress.get('estimated_total_time'))
        self.assertEqual(json_progress.get('remaining_seconds'), 0)

    @unittest.skipIf(django.VERSION[:2], (1, 0))
    def test_no_any_job_in_group(self):
        """Create group but no job create for that group.
        """
        group_name = 'test-ddrun'
        Group.objects.create(reference=group_name)
        test_url = self.URL + group_name + '/'

        response = self.client.get(test_url)
        self.assertEqual(response.status_code, 200)

        json = loads(response.content)
        self.assertEqual(json['_meta'],
            {'message': 'OK', 'status': 200, 'username': 'test'}
        )
        self.assertTrue(json.get('progress') is None)

    def test_no_group_valid_for_get_request(self):
        """ Do get request to non exist group.
        """
        #TODO need to catch more specific exception
        # now it just thrown TemplateDoesNotExist
        with self.assertRaises(Exception) as e:
            response = self.client.get(self.URL + 'fake-group/')
            self.assertEqual(response.status, 404)

    @unittest.skipIf(django.VERSION[:2], (1, 0))
    def test_all_jobs_executed(self):
        """Test get detail from group with all executed jobs.
        """
        group1 = Group.objects.create(reference='drun1')
        for i in range(5):
            Job.objects.create(name='j-%s' % i, args='[]', kwargs='{}',
                               meta='{}', priority=3, group=group1)
        for job in group1.jobs.all():
            job.executed = timezone.now()
            job.save()

        test_url = self.URL + 'drun1/'
        response = self.client.get(test_url)
        self.assertEqual(response.status_code, 200)

        json = loads(response.content)
        self.assertEqual(json['_meta'],
            {'message': 'OK', 'status': 200, 'username': 'test'})

        json_progress = json.get('progress')
        self.assertTrue(json_progress)
        self.assertEqual(json_progress.get('id'), group1.id)
        self.assertEqual(json_progress.get('created'), group1.created.isoformat())
        self.assertEqual(json_progress.get('latest_job_completed'),
                         group1.latest_executed_job().executed.isoformat())
        self.assertEqual(json_progress.get('total_jobs'), group1.jobs.count())
        self.assertEqual(json_progress.get('total_executed_jobs'), 5)
        self.assertEqual(json_progress.get('total_unexecuted_jobs'), 0)
        self.assertEqual(json_progress.get('total_error_jobs'), 0)

    @unittest.skipIf(django.VERSION[:2], (1, 0))
    def test_all_jobs_executed_with_error(self):
        """Test get detail from group with job errors.
        """
        group1 = Group.objects.create(reference='drun1')
        for i in range(5):
            Job.objects.create(name='j-%s' % i, args='[]', kwargs='{}',
                               meta='{}', priority=3, group=group1)
        for job in group1.jobs.all():
            job.executed = timezone.now() - timedelta(days=60)
            job.save()

        j1 = Job.objects.all()[0]
        j2 = Job.objects.all()[1]
        e1 = Error.objects.create(job=j1)
        e2 = Error.objects.create(job=j1)
        e3 = Error.objects.create(job=j2)

        test_url = self.URL + 'drun1/'
        response = self.client.get(test_url)
        self.assertEqual(response.status_code, 200)

        json = loads(response.content)
        self.assertEqual(json['_meta'],
            {'message': 'OK', 'status': 200, 'username': 'test'})

        json_progress = json.get('progress')
        self.assertTrue(json_progress)
        self.assertEqual(json_progress.get('id'), group1.id)
        self.assertEqual(json_progress.get('created'), group1.created.isoformat())
        self.assertEqual(json_progress.get('latest_job_completed'),
            group1.latest_executed_job().executed.isoformat())
        self.assertEqual(json_progress.get('total_jobs'), group1.jobs.count())
        self.assertEqual(json_progress.get('total_executed_jobs'), 5)
        self.assertEqual(json_progress.get('total_unexecuted_jobs'), 0)
        self.assertEqual(json_progress.get('total_error_jobs'), 2)

    @unittest.skipIf(django.VERSION[:2], (1, 0))
    def test_estimate_execution_duration_can_produce_result(self):
        """Just to test if estimate function produce result,
        not checking the result.
        """

        g1 = Group.objects.create(reference='test-group')
        g1.created = timezone.now() - timedelta(days=5000)
        g1.save()

        def create_job_series(id):
            j = Job.objects.create(
                name='job-%s' % id,
                args='[]',
                kwargs='{}',
                meta='{}',
                priority=5,
                group=g1
            )
            j.save()
            j.added = timezone.now() - timedelta(days=5000)
            j.save()
            return j

        self.assertIsNone(g1.latest_executed_job())

        j1, j2, j3, j4, j5, j6 = map(create_job_series, range(0, 6))
        j1.executed = j1.added + timedelta(days=10)
        j1.save()
        j2.executed = j2.added + timedelta(days=10)
        j2.save()

        total, remaining, consumed = g1.estimate_execution_duration()
        self.assertTrue(isinstance(total, timedelta))
        self.assertTrue(isinstance(remaining, timedelta))
        self.assertTrue(isinstance(consumed, timedelta))


    @unittest.skipIf(django.VERSION[:2], (1, 0))
    def test_estimate_execution_duration_with_no_job_valid(self):
        """Calculate function return None if no data for process.
        """
        g1 = Group.objects.create(reference='test-group')
        g1.created = timezone.now() - timedelta(days=5000)
        g1.save()

        total, remaining, consumed = g1.estimate_execution_duration()
        self.assertIsNone(total)
        self.assertIsNone(remaining)
        self.assertIsNone(consumed)

@unittest.skipIf(NoSlumber, True)
class TestHealth(WithUser, TestCase):
    URL = '/slumber/async/Job/health/'

    @unittest.skipIf(django.VERSION[:2], (1, 0))
    def test_get_wired(self):
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 200)
        json = loads(response.content)
        self.assertTrue(json.has_key('health'))

