"""
    Test for apis..
"""
from django.test import TestCase
from django.core import management

import datetime
from async import api
from async.models import Job, Group
from mock import patch, Mock


def get_today_dt():
    return datetime.datetime.today()


def get_d_before_today_by_days(d):
    return get_today_dt().date() - datetime.timedelta(days=d)


def get_d_before_dt_by_days(base_dt, d):
    return base_dt.date() - datetime.timedelta(days=d)


class TestRemoveOldJobs(TestCase):
    """Tests removing old jobs.
    """

    def setUp(self):
        def create_test_job(jid):
            return Job.objects.create(
                name='job-%s' % jid,
                args='[]',
                kwargs='{}',
                meta='{}',
                priority=5
            )

        self.create_job = create_test_job


    @patch('async.api.get_today_dt')
    def test_job_reschedule(self, mock_get_today_dt):
        today_dt = datetime.datetime.today()
        mock_get_today_dt.return_value = today_dt
        job_name = 'async.api.remove_old_jobs'

        # Run commands in func remove_old_jobs
        # when it's done will create new job with same name
        # and new schedule equal current + 8
        api.remove_old_jobs(1)
        self.assertEqual(Job.objects.filter(name=job_name).count(), 1)
        expected_job = Job.objects.get(name=job_name)

        # Check scheduled time of new job instance (which same name)
        # is more than current time = 8.0.
        diff = (
                   expected_job.scheduled - today_dt
               ).total_seconds()/3600.
        self.assertTrue(diff == 8.0)

        # Force first scheduled job to executed
        management.call_command('flush_queue')
        self.assertEqual(Job.objects.filter(name=job_name).count(), 1)

        new_expected_job = Job.objects.get(name=job_name)
        self.assertTrue(False)

    @patch('async.api.get_today_dt')
    def test_remove_jobs(self, mock_get_today_dt):
        mock_get_today_dt.return_value = datetime.datetime(2014, 1, 31)

        j1, j2, j3 = map(self.create_job, range(3))

        j1.executed = get_d_before_dt_by_days(datetime.datetime(2014, 1, 31),
                                              30)
        j1.save()

        j2.executed = get_d_before_dt_by_days(datetime.datetime(2014, 1, 31),
                                              15)
        j2.save()

        j3.executed = get_d_before_dt_by_days(datetime.datetime(2014, 1, 31),
                                              15)
        j3.save()

        api.remove_old_jobs(20)

        self.assertEqual(
            Job.objects.filter(name__in=['job-1', 'job-2']).count(), 2)

        mock_get_today_dt.return_value = datetime.datetime(2014, 4, 1)
        management.call_command('flush_queue')

        self.assertEqual(
            Job.objects.filter(name__in=['job-1', 'job-2']).count(), 0)
