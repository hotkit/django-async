"""
    Tests for the Slumber operations.
"""
from django.test import TestCase
from simplejson import loads


class TestSlumber(TestCase):
    """Make sure that Slumber is wired in properly.
    """
    maxDiff = None

    def test_slumber_root(self):
        """Make sure Slumber is properly wired in.
        """
        # Instance of 'WSGIRequest' has no 'status_code' member
        #  (but some types could not be inferred)
        # pylint: disable=E1103

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

