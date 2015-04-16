# -*- coding: utf-8 -*-
from django.test import TestCase
import async
from async.admin import display_group
from async.models import Group


class TestJobAdmin(TestCase):
    def do_nothing(self):
        return True

    def test_display_group__have_group(self):
        group = Group.latest_group_by_reference('nothing')
        job = async.schedule('async.tests.test_admin.TestJobAdmin.do_nothing', group=group)

        group_to_be_displayed = display_group(job)
        self.assertEqual(group_to_be_displayed, group.reference)

    def test_display_group__do_not_have_group(self):
        job = async.schedule('async.tests.test_admin.TestJobAdmin.do_nothing')

        group = display_group(job)
        self.assertEqual(group, None)
