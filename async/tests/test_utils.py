"""
    Extra tests that might be needed for utilities.
"""
from django.test import TestCase

from async.utils import object_at_end_of_path


class TestFetchingMethod(TestCase):
    """Tests for object_at_end_of_path
    """
    def test_with_global(self):
        """Make sure we can access a builtin
        """
        found = object_at_end_of_path('list')
        self.assertEqual(found, list)

