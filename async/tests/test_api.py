"""
    Test for apis..
"""
import django
from django.test import TestCase
from django.core import management
try:
    # No name 'timezone' in module 'django.utils'
    # pylint: disable=E0611
    from django.utils import timezone
except ImportError:
    from datetime import datetime as timezone

import datetime
import unittest

from async import api, stats
from async.models import Job, Group, Error
from mock import patch, Mock

NoSlumber = False
try:
    from slumber.server.meta import applications
except ImportError:
    NoSlumber = True


def get_now():
    return timezone.now()


def get_d_before_dt_by_days(base_dt, d):
    return base_dt - datetime.timedelta(days=d)


class TestGroupedAggregate(TestCase):

    @unittest.skipIf(django.VERSION[:2], (1, 0))
    def test_for_executed_jobs(self):
        job1 = TestRemoveOldJobs.create_job(1)
        job_started = timezone.now()
        job1.started = job_started
        job1.executed = job_started + datetime.timedelta(seconds=5)
        job1.save()

        job2 = TestRemoveOldJobs.create_job(2)
        job2.started = job_started
        job2.executed = job_started + datetime.timedelta(seconds=10)
        job2.save()

        job2_a = TestRemoveOldJobs.create_job(2)
        job2_a.started = job_started
        job2_a.cancelled = job_started
        job2_a.save()

        job1a = TestRemoveOldJobs.create_job(1)
        job1a.executed = job_started + datetime.timedelta(seconds=20)
        job1a.save()

        cancelled_jobs = api.get_grouped_aggregate(jobs_type='cancelled')
        self.assertEqual(cancelled_jobs[job2_a.name]['count'], 1)
        executed_jobs = api.get_grouped_aggregate(jobs_type='executed')
        self.assertEqual(executed_jobs[job1.name]['count'], 2)
        self.assertEqual(executed_jobs[job2.name]['count'], 1)
        unexecuted_jobs = api.get_grouped_aggregate(
            jobs_type='executed', complement=True)
        self.assertEquals(unexecuted_jobs[job2_a.name]['count'], 1)


@unittest.skipIf(NoSlumber, True)
class TestHealth(TestCase):
    """ Tests health of the queue.
    """
    def setUp(self):
        # Ensure we bootstrap Slumber's server side
        applications()


    def test_health_for_executed_jobs(self):
        job1 = TestRemoveOldJobs.create_job(1)
        job_started = timezone.now()
        job1.started = job_started
        job1.executed = job_started + datetime.timedelta(seconds=5)
        job1.save()

        job2 = TestRemoveOldJobs.create_job(2)
        job2.started = job_started
        job2.executed = job_started + datetime.timedelta(seconds=10)
        job2.save()

        job2_a = TestRemoveOldJobs.create_job(2)
        job2_a.started = job_started
        job2_a.save()

        TestRemoveOldJobs.create_job(1)

        queue_health = api.health().get('queue', None)

        self.assertEquals(queue_health['not-executed'], 2)
        self.assertEquals(queue_health['executed'], 2)
        self.assertEquals(queue_health['oldest-executed'],
            '/slumber/async/Job/data/%s/' % job1.pk)
        self.assertEquals(queue_health['most-recent-executed'],
            '/slumber/async/Job/data/%s/' % job2.pk)


    def test_health_for_not_executed_jobs(self):
        TestRemoveOldJobs.create_job(1)
        TestRemoveOldJobs.create_job(2)

        queue_health = api.health().get('queue', None)

        self.assertEquals(queue_health['not-executed'], 2)
        self.assertEquals(queue_health['executed'], 0)
        self.assertEquals(queue_health['cancelled'], 0)



    def test_health_for_cancelled_jobs(self):
        dt_now = timezone.now()
        job1 = TestRemoveOldJobs.create_job(1)
        job1.cancelled = dt_now
        job1.save()

        job2 = TestRemoveOldJobs.create_job(2)
        job2.cancelled = dt_now + datetime.timedelta(seconds=10)
        job2.save()

        TestRemoveOldJobs.create_job(2)
        TestRemoveOldJobs.create_job(1)

        queue_health = api.health().get('queue', None)

        self.assertEquals(queue_health['cancelled'], 2)
        self.assertEquals(queue_health['oldest-cancelled'],
            '/slumber/async/Job/data/%s/' % job1.pk)
        self.assertEquals(queue_health['most-recent-cancelled'],
            '/slumber/async/Job/data/%s/' % job2.pk)


    def test_health_for_errors(self):
        dt_now = timezone.now()
        job1 = api.schedule('job-1', group=None)
        error1 = Error.objects.create(job=job1, executed=dt_now, exception="First", traceback="None")

        dt_now = dt_now + datetime.timedelta(seconds=10)
        error2 = Error.objects.create(job=job1, executed=dt_now, exception="Second", traceback="None")

        queue_errors = api.health().get('errors', None)

        self.assertEquals(queue_errors['number'], 2)


    @patch('async.stats._get_now')
    def test_health_for_queue_completion_estimates(self, mock_now):
        mock_now.return_value = timezone.now()
        job = TestRemoveOldJobs.create_job(1)
        queue_health = api.health(stats.estimate_queue_completion).get('queue', None)
        self.assertEquals(queue_health['estimated-completion-current-job'], 0)
        self.assertEquals(queue_health['estimated-completion'], 0)

        job_started = mock_now.return_value - datetime.timedelta(seconds=9)
        job.started = job_started
        job.executed = job_started + datetime.timedelta(seconds=5)
        job.save()

        queue_health = api.health(stats.estimate_queue_completion).get('queue', None)
        self.assertEquals(queue_health['estimated-completion-current-job'], 0)
        self.assertEquals(queue_health['estimated-completion'], 0)

        job2 = TestRemoveOldJobs.create_job(1)
        job2.started = mock_now.return_value - datetime.timedelta(seconds=3)
        job2.save()

        #queue_health = api.health().get('queue', None)
        queue_health = api.health(stats.estimate_queue_completion).get('queue', None)
        self.assertAlmostEqual(queue_health['estimated-completion-current-job'], 2.0)
        self.assertAlmostEqual(queue_health['estimated-completion'], 2.0)



class TestRemoveOldJobs(TestCase):
    """Tests removing old jobs.
    """
    @staticmethod
    def create_job(jid, group=None):
        job = api.schedule('job-%s' % jid, group=group)
        Error.objects.create(job=job, exception='Error', traceback='code stack')
        return job

    @patch('async.api._get_now')
    def test_job_reschedule_duration(self, mock_get_today_dt):
        """Test if next schedule with run in 8 hrs
        """

        today_dt = timezone.now()
        mock_get_today_dt.return_value = today_dt
        job_name = 'async.api.remove_old_jobs'

        # Run commands in func remove_old_jobs
        # when it's done will create new job with same name
        # and new schedule equal current + 8
        api.remove_old_jobs(2)

        self.assertEqual(Job.objects.filter(name=job_name).count(), 1)
        expected_job = Job.objects.get(name=job_name)
        self.assertIsNotNone(expected_job.scheduled)

        # Check scheduled time of new job instance (which same name)
        # is more than current time = 8.0.
        diff = (expected_job.scheduled - today_dt).total_seconds()/3600.
        self.assertTrue(diff == 8.0)

    @patch('async.api._get_now')
    def test_job_reschedule(self, mock_get_today_dt):
        """Test deal with only remove_old_jobs job
        - it should remove old remove_old_jobs job
        - it should get new reschedule remove_old_jobs job
        """

        today_dt = timezone.now()
        mock_get_today_dt.return_value = today_dt
        job_name = 'async.api.remove_old_jobs'

        # Run commands in func remove_old_jobs
        # when it's done will create new job with same name
        # and new schedule equal current + 8
        api.remove_old_jobs(2)

        self.assertEqual(Job.objects.filter(name=job_name).count(), 1)

        # Force first job to execute (no scheduled set it's run immediately).
        expected_job = Job.objects.get(name=job_name)
        expected_job.scheduled = None
        expected_job.save()
        management.call_command('flush_queue')

        self.assertEqual(Job.objects.all().count(), 2)
        self.assertEqual(Job.objects.filter(name=job_name).count(), 2)

        # Force first scheduled job to executed
        # (no scheduled set it's run immediately).
        latest_job = Job.objects.filter(name=job_name).latest('id')
        latest_job.scheduled = None
        latest_job.save()
        management.call_command('flush_queue')

        # Force latest job to execute (no scheduled set it's run immediately).
        latest_job = Job.objects.filter(name=job_name).latest('id')
        latest_job.scheduled = None
        latest_job.save()

        # Get ids from job that gonna be remove
        # these ids will be check after latest job was executed.
        jobs_must_gone_ids = []
        for j in Job.objects.filter(name=job_name):
            if j.executed is not None:
                j.executed = j.executed - datetime.timedelta(days=5)
                j.save()
                jobs_must_gone_ids.append(j.id)
        management.call_command('flush_queue')

        # Current jobs should be valid only
        # - latest remove_old_jobs that does not execute yet -> 1
        # - latest remove_old_jobs that was executed -> 1
        not_expected_result = filter(
            lambda x: x in jobs_must_gone_ids,
            Job.objects.filter(name=job_name).values_list('id', flat=True)
        )
        self.assertEqual(len(list(not_expected_result)), 0)
        self.assertEqual(Job.objects.filter(name=job_name).count(), 2)
        self.assertEqual(
            Job.objects.filter(name=job_name, executed__isnull=False).count(),
            1)
        self.assertEqual(
            Job.objects.filter(name=job_name, executed__isnull=True).count(), 1)

    @patch('async.api._get_now')
    def test_remove_jobs(self, mock_get_today_dt):
        """ job name job-0 must be removed after flush_queue run.
        """
        mock_get_today_dt.return_value = (
            get_now() - datetime.timedelta(days=60))

        j1, j2, j3 = map(self.create_job, range(3))

        j1.executed = get_d_before_dt_by_days(
            mock_get_today_dt.return_value, 30)
        j1.save()
        j2.executed = get_d_before_dt_by_days(
            mock_get_today_dt.return_value, 15)
        j2.save()
        j3.executed = get_d_before_dt_by_days(
            mock_get_today_dt.return_value, 15)
        j3.save()

        api.remove_old_jobs(20)

        self.assertEqual(
            Job.objects.filter(name__in=['job-1', 'job-2']).count(), 2)

        mock_get_today_dt.return_value = get_now()
        management.call_command('flush_queue')

        self.assertEqual(
            Job.objects.filter(name__in=['job-1', 'job-2']).count(), 0)

    @patch('async.api._get_now')
    def test_remove_old_job_with_no_param_sent(self, mock_get_today_dt):
        """Test in case of no parameter sent to remove_old_jobs
        """
        test_base_dt = get_now() - datetime.timedelta(days=60)
        mock_get_today_dt.return_value = test_base_dt

        j1, j2 = map(self.create_job, range(2))
        j1.executed = test_base_dt - datetime.timedelta(days=31)
        j1.save()

        j2.executed = test_base_dt - datetime.timedelta(days=20)
        j2.save()

        self.assertEqual(Error.objects.all().count(), 2)

        api.remove_old_jobs()

        # Should get remove_old_jobs for next round and j2
        # j1 should gone now

        self.assertEqual(Job.objects.all().count(), 2)
        self.assertIsNotNone(Job.objects.filter(name=j2.name))
        self.assertEqual(Error.objects.all().count(), 1, Error.objects.all())

    def test_get_now(self):
        result = api._get_now()
        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, datetime.datetime))

    def test_groups__with_unexecuted_are_not_removed(self):
        test_base_dt = get_now()
        group = Group.objects.create(reference='no-rm-group')
        job = self.create_job('no-rm-group', group)

        api.remove_old_jobs()

        self.assertEqual(Job.objects.all().count(), 2, Job.objects.all())
        self.assertEqual(Group.objects.all().count(), 1, Group.objects.all())
        self.assertEqual(Error.objects.all().count(), 1, Error.objects.all())

    def test_groups_with_executed_job_are_removed(self):
        test_base_dt = get_now()
        group = Group.objects.create(reference='rm-group')
        job = self.create_job('rm-group', group)
        job.executed = test_base_dt - datetime.timedelta(days=31)
        job.save()

        api.remove_old_jobs()

        self.assertEqual(Job.objects.all().count(), 1, Job.objects.all())
        self.assertEqual(Job.objects.all()[0].name, 'async.api.remove_old_jobs')
        self.assertEqual(Group.objects.all().count(), 0, Group.objects.all())
        self.assertEqual(Error.objects.all().count(), 0, Error.objects.all())

    def test_groups__with_young_jobs_are_not_removed(self):
        test_base_dt = get_now()
        group = Group.objects.create(reference='not_rm-young-group')
        job = self.create_job('not_rm-young-group', group)
        job.executed = test_base_dt - datetime.timedelta(days=16)
        job.save()

        api.remove_old_jobs()

        self.assertEqual(Job.objects.all().count(), 2, Job.objects.all())
        self.assertEqual(Group.objects.all().count(), 1, Group.objects.all())
        self.assertEqual(Error.objects.all().count(), 1, Error.objects.all())

    def test_groups__with_young_and_old_jobs_are_not_removed(self):
        test_base_dt = get_now()
        group = Group.objects.create(reference='not_rm-mixed-group')
        job1 = self.create_job('not_rm-mixed-group', group)
        job2 = self.create_job('not_rm-mixed-group', group)

        job1.executed = test_base_dt - datetime.timedelta(days=45)
        job1.save()
        job2.executed = test_base_dt - datetime.timedelta(days=16)
        job2.save()

        api.remove_old_jobs()

        self.assertEqual(Job.objects.all().count(), 3, Job.objects.all())
        self.assertEqual(Group.objects.all().count(), 1, Group.objects.all())
        self.assertEqual(Error.objects.all().count(), 2, Error.objects.all())

    @patch('async.api._get_now')
    def test_remove__cancelled_jobs(self, mock_get_today_dt):
        """ job name job-0 must be removed after flush_queue run.
        """
        mock_get_today_dt.return_value = (
            get_now() - datetime.timedelta(days=60))

        j1, j2, j3 = map(self.create_job, range(3))

        j1.cancelled = get_d_before_dt_by_days(
            mock_get_today_dt.return_value, 30)
        j1.save()
        j2.cancelled = get_d_before_dt_by_days(
            mock_get_today_dt.return_value, 15)
        j2.save()
        j3.cancelled = get_d_before_dt_by_days(
            mock_get_today_dt.return_value, 15)
        j3.save()

        api.remove_old_jobs(20)

        self.assertEqual(
            Job.objects.filter(name__in=['job-1', 'job-2']).count(), 2)

        mock_get_today_dt.return_value = get_now()
        management.call_command('flush_queue')

        self.assertEqual(
            Job.objects.filter(name__in=['job-1', 'job-2']).count(), 0)

    @patch('async.api._get_now')
    def test_remove__mixing_jobs(self, mock_get_today_dt):
        """ job name job-0 must be removed after flush_queue run.
        """
        mock_get_today_dt.return_value = (
            get_now() - datetime.timedelta(days=60))

        j1, j2, j3, j4, j5, j6 = map(self.create_job, range(6))

        j1.executed = get_d_before_dt_by_days(
            mock_get_today_dt.return_value, 30)
        j1.save()
        j2.executed = get_d_before_dt_by_days(
            mock_get_today_dt.return_value, 15)
        j2.save()
        j3.executed = get_d_before_dt_by_days(
            mock_get_today_dt.return_value, 15)
        j3.save()
        j4.cancelled = get_d_before_dt_by_days(
            mock_get_today_dt.return_value, 30)
        j4.save()
        j5.cancelled = get_d_before_dt_by_days(
            mock_get_today_dt.return_value, 15)
        j5.save()
        j6.cancelled = get_d_before_dt_by_days(
            mock_get_today_dt.return_value, 15)
        j6.save()

        api.remove_old_jobs()

        self.assertEqual(
            Job.objects.filter(name__in=['job-1', 'job-2', 'job-3', 'job-4', 'job-5', 'job-6']).count(), 5)

        mock_get_today_dt.return_value = get_now()
        management.call_command('flush_queue')

        self.assertEqual(
            Job.objects.filter(name__in=['job-1', 'job-2', 'job-3', 'job-4', 'job-5', 'job-6']).count(), 0)

    def test_groups__with_young_cancelled_jobs_are_not_removed(self):
        test_base_dt = get_now()
        group = Group.objects.create(reference='not_rm-young-group')
        job = self.create_job('not_rm-young-group', group)
        job.cancelled = test_base_dt - datetime.timedelta(days=16)
        job.save()

        api.remove_old_jobs()

        self.assertEqual(Job.objects.all().count(), 2, Job.objects.all())
        self.assertEqual(Group.objects.all().count(), 1, Group.objects.all())
        self.assertEqual(Error.objects.all().count(), 1, Error.objects.all())

    def test_groups_with_cancelled_job_are_removed(self):
        test_base_dt = get_now()
        group = Group.objects.create(reference='rm-group')
        job = self.create_job('rm-group', group)
        job.cancelled = test_base_dt - datetime.timedelta(days=31)
        job.save()

        api.remove_old_jobs()

        self.assertEqual(Job.objects.all().count(), 1, Job.objects.all())
        self.assertEqual(Job.objects.all()[0].name, 'async.api.remove_old_jobs')
        self.assertEqual(Group.objects.all().count(), 0, Group.objects.all())
        self.assertEqual(Error.objects.all().count(), 0, Error.objects.all())

    def test_groups__with_young_and_old_cancelled_jobs_are_not_removed(self):
        test_base_dt = get_now()
        group = Group.objects.create(reference='not_rm-mixed-group')
        job1 = self.create_job('not_rm-mixed-group', group)
        job2 = self.create_job('not_rm-mixed-group', group)

        job1.cancelled = test_base_dt - datetime.timedelta(days=45)
        job1.save()
        job2.cancelled = test_base_dt - datetime.timedelta(days=16)
        job2.save()

        api.remove_old_jobs()

        self.assertEqual(Job.objects.all().count(), 3, Job.objects.all())
        self.assertEqual(Group.objects.all().count(), 1, Group.objects.all())
        self.assertEqual(Error.objects.all().count(), 2, Error.objects.all())
