"""
    Tests for the Slumber operations.
"""
from django.contrib.auth.models import User, Permission
from django.test import TestCase
from simplejson import loads

from async.models import Job


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
                'django_nose': '/slumber/django_nose/'},
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
        json = loads(response.content)
        self.assertEqual(json, dict(
            job=dict(id=job.id),
            _meta={'message': 'OK', 'status': 200, 'username': 'test'}))

