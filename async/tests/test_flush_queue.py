"""
    Tests for the flush queue management command.
"""
from django.test import TestCase
from django.core import management

from async.api import schedule
from async.models import Job, Group


def do_job():
    pass

def do_job2():
    pass

class TestFlushQueue(TestCase):
    def setUp(self):
        self.group = Group.objects.create(reference='1of2')
        self.j1 = schedule(do_job, group=self.group)
        self.j2 = schedule(do_job, group=self.group)
        self.j3 = schedule(do_job2, group=self.group)

    def test_0of2(self):
        management.call_command('flush_queue', which=0, outof=2)
        j1 = Job.objects.get(pk=self.j1.pk)
        j2 = Job.objects.get(pk=self.j2.pk)
        if ( j1.pk %2 ):
            self.assertIsNone(j1.executed)
            self.assertIsNotNone(j2.executed)
        else:
            self.assertIsNotNone(j1.executed)
            self.assertIsNone(j2.executed)

    def test_1of2(self):
        management.call_command('flush_queue', which=1, outof=2)
        j1 = Job.objects.get(pk=self.j1.pk)
        j2 = Job.objects.get(pk=self.j2.pk)
        if ( j1.pk %2 ):
            self.assertIsNotNone(j1.executed)
            self.assertIsNone(j2.executed)
        else:
            self.assertIsNone(j1.executed)
            self.assertIsNotNone(j2.executed)

    def test_2of2(self):
        management.call_command('flush_queue', which=2, outof=2)
        j1 = Job.objects.get(pk=self.j1.pk)
        j2 = Job.objects.get(pk=self.j2.pk)
        if ( j1.pk %2 ):
            self.assertIsNone(j1.executed)
            self.assertIsNotNone(j2.executed)
        else:
            self.assertIsNotNone(j1.executed)
            self.assertIsNone(j2.executed)

    def test_namefilter(self):
        management.call_command('flush_queue', filter='async.tests.test_flush_queue.do_job2')
        j1 = Job.objects.get(pk=self.j1.pk)
        j3 = Job.objects.get(pk=self.j3.pk)
        self.assertIsNone(j1.executed)
        self.assertIsNotNone(j3.executed)

class TestFinalJob(TestCase):
    def test_final_when_added_last(self):
        self.group = Group.objects.create(reference='final-job')
        self.j1 = schedule(do_job, group=self.group)
        self.j2 = schedule(do_job, group=self.group)
        self.j3 = schedule(do_job)
        self.group.on_completion(self.j3)
        management.call_command('flush_queue')
        j1 = Job.objects.get(pk=self.j1.pk)
        j2 = Job.objects.get(pk=self.j2.pk)
        j3 = Job.objects.get(pk=self.j3.pk)
        self.assertLess(j1.executed, j2.executed)
        self.assertLess(j2.executed, j3.executed)

    def test_final_when_added_first(self):
        self.j1 = schedule(do_job)
        self.group = Group.objects.create(reference='final-job', final=self.j1)
        self.j2 = schedule(do_job, group=self.group)
        self.j3 = schedule(do_job, group=self.group)
        management.call_command('flush_queue')
        j1 = Job.objects.get(pk=self.j1.pk)
        j2 = Job.objects.get(pk=self.j2.pk)
        j3 = Job.objects.get(pk=self.j3.pk)
        self.assertLess(j2.executed, j3.executed)
        self.assertLess(j3.executed, j1.executed)

    def test_only_has_final_job(self):
        self.j1 = schedule(do_job)
        self.group = Group.objects.create(reference='final-job', final=self.j1)
        management.call_command('flush_queue')
        j1 = Job.objects.get(pk=self.j1.pk)
        self.assertIsNotNone(j1.executed)

