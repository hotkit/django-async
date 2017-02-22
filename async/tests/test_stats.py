import django
from django.test import TestCase
try:
    # No name 'timezone' in module 'django.utils'
    # pylint: disable=E0611
    from django.utils import timezone
except ImportError:
    from datetime import datetime as timezone

import datetime
import unittest

from async import stats, api
from async.models import Group, Error
from mock import patch

def create_job(jid, group=None):
    job = api.schedule('job-%s' % jid, group=group)
    Error.objects.create(job=job, exception='Error', traceback='code stack')
    return job


class TestStats(TestCase):
    """Tests statsistics of the queue.
    """

    @patch('async.stats._get_now')
    def test_estimate_completion_time_for_ungrouped_jobs(self, mock_now):
        job_started = timezone.now()
        mock_now.return_value = job_started

        job1 = create_job(1)
        job1.started = job_started
        job1.executed = job_started + datetime.timedelta(seconds=5)
        job1.save()

        job2 = create_job(2)
        job2.started = job_started
        job2.executed = job_started + datetime.timedelta(seconds=10)
        job2.save()

        job2 = create_job(2)
        job2.started = job_started
        job2.executed = job_started + datetime.timedelta(seconds=8.4)
        job2.save()

        create_job(1)
        create_job(2)
        create_job(1)
        self.assertAlmostEqual(stats._estimate_completion_ungrouped(), 19.2, 1)
        self.assertAlmostEqual(stats.estimate_queue_completion(), 19.2, 1)

    @unittest.skipIf(django.VERSION[:2], (1, 0))
    @patch('async.stats._get_now')
    def test_estimate_completion_time_for_all_jobs(self, mock_now):
        job_started = timezone.now()
        mock_now.return_value = job_started

        job1 = create_job(1)
        job_started = timezone.now()
        job1.started = job_started
        job1.executed = job_started + datetime.timedelta(seconds=5)
        job1.save()

        job2 = create_job(2)
        job2.started = job_started
        job2.executed = job_started + datetime.timedelta(seconds=10)
        job2.save()

        job3 = create_job(1, group="a")
        job_started = timezone.now()
        job3.started = job_started
        job3.executed = job_started + datetime.timedelta(seconds=5)
        job3.save()

        create_job(1, group="a")
        create_job(2)
        self.assertAlmostEqual(stats.estimate_queue_completion(), 15.0, 1)

    @patch('async.stats._get_now')
    def test_estimate_current_job_completion(self, mock_now):
        job_started = timezone.now() - datetime.timedelta(seconds=30)
        mock_now.return_value = job_started + datetime.timedelta(seconds=30)
        job = create_job(1)
        self.assertEquals(stats.estimate_current_job_completion(), 0)

        job.started = job_started
        job.executed = job_started + datetime.timedelta(seconds=5)
        job.save()
        self.assertAlmostEqual(stats.estimate_current_job_completion(), 0, 1)

        job2 = create_job(1)
        job2.started = mock_now.return_value - datetime.timedelta(seconds=3)
        job2.save()
        self.assertAlmostEqual(stats.estimate_current_job_completion(), 2.0, 1)

    @patch('async.stats._get_now')
    def test_estimate_rough_queue_completion(self, mock_now):
        job_started = timezone.now()
        mock_now.return_value = job_started

        job1a = create_job(1)
        job1a_started = job_started - datetime.timedelta(hours=7)
        job1a.started = job1a_started
        job1a.scheduled = job1a_started
        job1a.executed = job1a_started + datetime.timedelta(seconds=5)
        job1a.save()

        job1b = create_job(11)
        job1b_started = job_started - datetime.timedelta(hours=7, seconds=10)
        job1b.started = job1b_started
        job1b.scheduled = job1b_started - datetime.timedelta(seconds=3)
        job1b.executed = job1b_started + datetime.timedelta(seconds=7)
        job1b.save()

        job2a = create_job(2)
        job2a_started = job_started - datetime.timedelta(hours=7, seconds=20)
        job2a.started = job2a_started
        job2a.executed = job2a_started + datetime.timedelta(seconds=25)
        job2a.save()

        create_job(2)

        self.assertEquals(stats.estimate_rough_queue_completion(), 13.33)
