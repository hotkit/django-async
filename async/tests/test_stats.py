from django.test import TestCase
try:
    # No name 'timezone' in module 'django.utils'
    # pylint: disable=E0611
    from django.utils import timezone
except ImportError:
    from datetime import datetime as timezone

import datetime

from async import stats, api
from async.models import Error
from mock import patch

def create_job(jid, group=None):
    job = api.schedule('job-%s' % jid, group=group)
    Error.objects.create(job=job, exception='Error', traceback='code stack')
    return job


class TestStats(TestCase):
    """Tests statsistics of the queue.
    """

    def test_estimate_completion_time_for_ungrouped_jobs(self):
        job1 = create_job(1)
        job_started = timezone.now()
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
        self.assertEquals(stats._estimate_completion_ungrouped(), 19.2)
        self.assertEquals(stats.estimate_queue_completion(), 19.2)

    def test_estimate_completion_time_for_grouped_jobs(self):
        job1 = create_job(1, group="a")
        job_started = timezone.now()
        job1.started = job_started
        job1.executed = job_started + datetime.timedelta(seconds=5)
        job1.save()

        job2 = create_job(2, group="b")
        job2.started = job_started
        job2.executed = job_started + datetime.timedelta(seconds=10)
        job2.save()

        job2 = create_job(2, group="b")
        job2.started = job_started
        job2.executed = job_started + datetime.timedelta(seconds=8.4)
        job2.save()

        create_job(1, group="a")
        create_job(2, group="b")
        create_job(1, group="a")
        self.assertEquals(stats.estimate_queue_completion(), 23.38)

    def test_estimate_completion_time_for_all_jobs(self):
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
        self.assertEquals(stats.estimate_queue_completion(), 15.0)

    @patch('async.stats._get_now')
    def test_estimate_current_job_completion(self, mock_now):
        mock_now.return_value = datetime.datetime(2099, 12, 31, 23, 59, 59)
        job = create_job(1)
        self.assertEquals(stats.estimate_current_job_completion(), None)

        job_started = datetime.datetime(2099, 12, 31, 23, 59, 50)
        job.started = job_started
        job.executed = job_started + datetime.timedelta(seconds=5)
        job.save()
        self.assertEquals(stats.estimate_current_job_completion(), None)

        job2 = create_job(1)
        job2.started = datetime.datetime(2099, 12, 31, 23, 59, 56)
        job2.save()
        self.assertEquals(stats.estimate_current_job_completion(), 2.0)
