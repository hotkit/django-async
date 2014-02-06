"""
    Tests for the Slumber operations.
"""
from datetime import datetime
from django.contrib.auth.models import User, Permission
from django.test import TestCase
from simplejson import dumps, loads
from django.core.exceptions import ValidationError

from async.models import Job, Group, Error


# Instance of 'WSGIRequest' has no 'status_code' member
#  (but some types could not be inferred)
# pylint: disable=E1103


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
        self.assertEqual(json, dict(
            services=None,
            configuration={},
            apps={
                'async': '/slumber/async/',
                'django.contrib.sites': '/slumber/django/contrib/sites/',
                'django.contrib.admin': '/slumber/django/contrib/admin/',
                'django.contrib.auth': '/slumber/django/contrib/auth/',
                'django.contrib.contenttypes':
                    '/slumber/django/contrib/contenttypes/',
                'django.contrib.messages': '/slumber/django/contrib/messages/',
                'django.contrib.sessions': '/slumber/django/contrib/sessions/',
                'django.contrib.staticfiles':
                    '/slumber/django/contrib/staticfiles/',
                'django_nose': '/slumber/django_nose/',
                'south': '/slumber/south/'},
            _meta={'message': 'OK', 'status': 200}))


class TestSchedule(TestCase):
    """Make sure the schedule API wrapper works.
    """
    URL = '/slumber/async/Job/schedule/'
    def setUp(self):
        super(TestSchedule, self).setUp()
        self.user = User.objects.create(username='test')
        self.user.set_password('password')
        self.user.save()
        self.client.login(username='test', password='password')
        self.permission = Permission.objects.get(codename='add_job')
        self.user.user_permissions.add(self.permission)

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
        response = self.client.post(self.URL, dict(
            name='test-job-1', run_after='2011-04-12 14:12:43'))
        self.assertEqual(response.status_code, 200)
        job = Job.objects.get(name='test-job-1')
        self.assertEqual(job.args, '[]')
        self.assertEqual(job.scheduled, datetime(2011, 4, 12, 14, 12, 43))
        json = loads(response.content)
        self.assertEqual(json, dict(
            job=dict(id=job.id),
            _meta={'message': 'OK', 'status': 200, 'username': 'test'}))

    def test_create_job_with_group(self):
        """Create job with group reference.
        """
        group = Group.objects.create(
                reference='test-group-1',
                description='info'
            )
        response = self.client.post(self.URL, dict(
                name='test-job-1',
                run_after='2011-04-12 14:12:23',
                group=group.reference
            )
        )
        self.assertEqual(response.status_code, 200)
        job = Job.objects.get(name='test-job-1')
        self.assertEqual(job.group.reference, group.reference)

    def test_create_job_with_non_exist_group(self):
        """Create job with non exist group
        """
        response = self.client.post(self.URL, dict(
                name='test-job-1',
                run_after='2011-04-12 14:12:23',
                group='non-exist-group'
            )
        )
        self.assertEqual(response.status_code, 404)
        json = loads(response.content)
        self.assertEqual(json, dict(
                _meta={
                    'status': 404,
                    'username': 'test',
                    'message': 'Not Found'
                },
                error='Group matching query does not exist.'
            )
        )

    def test_create_job_with_multiple_group_same_reference(self):
        """Create job by assiging multiple group
        current job should has been assign by latest group
        """
        g1 = Group.objects.create(reference='multiple-group')
        g2 = Group.objects.create(reference='multiple-group')
        g3 = Group.objects.create(reference='multiple-group')
        response = self.client.post(self.URL, dict(
            name='test-job-1',
            run_after='2011-04-12 14:12:23',
            group='multiple-group'
        )
        )
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
        g1 = Group.objects.create(reference='test-group')

        j1 = Job.objects.create(
            name='test-job-1',
            args='[]',
            kwargs='{}',
            meta='{}',
            priority=5,
            group=g1
        )
        j1.executed = datetime(2014, 1, 1)
        j1.save()
        with self.assertRaises(ValidationError) as e:
            response = self.client.post(self.URL, dict(
                name='test-job-2',
                run_after='2011-04-12 14:12:23',
                group='test-group'
            )
            )


class TestProgress(TestCase):
    URL = '/slumber/async/Group/progress/'

    def setUp(self):
        super(TestProgress, self).setUp()
        self.user = User.objects.create(username='test')
        self.user.set_password('password')
        self.user.save()
        self.client.login(username='test', password='password')
        self.permission = Permission.objects.get(codename='add_job')
        self.user.user_permissions.add(self.permission)

    def test_get_work(self):
        """Test normol get request work.
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
        self.assertEqual(json_progress.get('created'), str(group1.created))
        self.assertIsNone(json_progress.get('last_job_completed'))
        self.assertEqual(json_progress.get('total_jobs'), group1.jobs.count())
        self.assertEqual(json_progress.get('total_executed_jobs'), 0)
        self.assertEqual(json_progress.get('total_unexecuted_jobs'), 2)
        self.assertEqual(json_progress.get('total_error_jobs'), 0)
        self.assertIsNone(json_progress.get('estimated_time_finishing'))

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

    def test_all_jobs_executed(self):
        """Test get detail from group with all executed jobs.
        """
        from async.slumber_operations import Progress

        group1 = Group.objects.create(reference='drun1')
        for i in range(5):
            Job.objects.create(name='j-%s' % i, args='[]', kwargs='{}', meta='{}', priority=3, group=group1)
        for job in group1.jobs.all():
            job.executed=datetime(2014,1,1)
            job.save()

        test_url = self.URL + 'drun1/'
        response = self.client.get(test_url)
        self.assertEqual(response.status_code, 200)

        json = loads(response.content)
        self.assertEqual(json['_meta'],
            {'message': 'OK', 'status': 200, 'username': 'test'}
        )

        json_progress = json.get('progress')
        self.assertTrue(json_progress)
        self.assertEqual(json_progress.get('id'), group1.id)
        self.assertEqual(json_progress.get('created'), str(group1.created))
        self.assertEqual(json_progress.get('last_job_completed'), str(Progress.latest_executed_job_time(group1)))
        self.assertEqual(json_progress.get('total_jobs'), group1.jobs.count())
        self.assertEqual(json_progress.get('total_executed_jobs'), 5)
        self.assertEqual(json_progress.get('total_unexecuted_jobs'), 0)
        self.assertEqual(json_progress.get('total_error_jobs'), 0)
        self.assertEqual(json_progress.get('estimated_group_duration'), str(Progress.estimate_execution_duration(group1)))

    def test_all_jobs_executed_with_error(self):
        """Test get detail from group with job errors.
        """
        from async.slumber_operations import Progress

        group1 = Group.objects.create(reference='drun1')
        for i in range(5):
            Job.objects.create(name='j-%s' % i, args='[]', kwargs='{}', meta='{}', priority=3, group=group1)
        for job in group1.jobs.all():
            job.executed=datetime(2014,1,1)
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
            {'message': 'OK', 'status': 200, 'username': 'test'}
        )

        json_progress = json.get('progress')
        self.assertTrue(json_progress)
        self.assertEqual(json_progress.get('id'), group1.id)
        self.assertEqual(json_progress.get('created'), str(group1.created))
        self.assertEqual(json_progress.get('last_job_completed'), str(Progress.latest_executed_job_time(group1)))
        self.assertEqual(json_progress.get('total_jobs'), group1.jobs.count())
        self.assertEqual(json_progress.get('total_executed_jobs'), 5)
        self.assertEqual(json_progress.get('total_unexecuted_jobs'), 0)
        self.assertEqual(json_progress.get('total_error_jobs'), 2)
        self.assertEqual(json_progress.get('estimated_group_duration'), str(Progress.estimate_execution_duration(group1)))
