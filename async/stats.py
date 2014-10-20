"""
   Provide stats and estimates about the queue
"""
from async.models import Group, Job
from datetime import timedelta
try:
    # No name 'timezone' in module 'django.utils'
    # pylint: disable=E0611
    from django.utils import timezone
except ImportError: # pragma: no cover
    from datetime import datetime as timezone


def _get_now():
    """Get today datetime, testing purpose.
    """
    return timezone.now()


def estimate_rough_queue_completion():
    """ Roughly estimate the remaining execution time for the queue,
        assuming that there is no waiting time.

        Ignore idle time because it overweights the average when
        number of upcoming jobs are less.
    """
    executed_jobs_since_yesterday = Job.objects.filter(executed__gt=_get_now()
                                                       - timedelta(days=1))\
                                               .order_by('scheduled')
    total_executed = executed_jobs_since_yesterday.count()
    total_execution_time, total_waiting_time = 0, 0

    for job in executed_jobs_since_yesterday:
        delta = job.executed - job.started
        total_execution_time += float(delta.total_seconds())
        if job.scheduled:
            delta_waiting = job.started - job.scheduled
            total_waiting_time += delta_waiting.total_seconds()

    avg_runtime = total_execution_time / (total_executed or 1)
    avg_wait_time = total_waiting_time / (total_executed or 1)
    remaining_jobs_count = Job.objects.filter(executed__isnull=True,
                                              started__isnull=True,
                                              cancelled__isnull=True).count()
    return round(remaining_jobs_count * (avg_runtime + avg_wait_time), 2)


def estimate_current_job_completion():
    """ Estimate remaining completion time current job based on
        average of previous runs

        Returns a floating value representing time in seconds
    """
    try:
        job = Job.objects.get(executed__isnull=True, cancelled__isnull=True,
                              started__isnull=False)
        similar_executed_jobs = Job.objects.filter(name=job.name,
                                                   executed__isnull=False,
                                                   cancelled__isnull=True,
                                                   group__isnull=True)
        total_execution_time = 0
        for similar_job in similar_executed_jobs:
            delta = similar_job.executed - similar_job.started
            total_execution_time += float(delta.total_seconds())
        average_runtime = total_execution_time / \
                          (similar_executed_jobs.count() or 1)
        time_spent = _get_now() - job.started
        projection = average_runtime - time_spent.total_seconds()
        return round(projection, 2)
    except Job.DoesNotExist:
        return 0


def estimate_queue_completion():
    """Estimate average time (in seconds) that the queue
       will take to execute

       Return floating point value indicating average time
       for completion of all jobs in the queue

       Does not account for idle and waiting time
    """
    total_estimated = 0
    for group in Group.objects.all():
        estimated, _, _ = group.estimate_execution_duration()
        if isinstance(estimated, timedelta):
            total_estimated += estimated.total_seconds()
    return round(total_estimated + estimate_current_job_completion() +
                 _estimate_completion_ungrouped(), 2)


def _estimate_completion_ungrouped():
    """ Estimation for jobs that do not belong to group

        Return floating point value indicating average time
        for completion of ungrouped jobs in queue.
    """
    remaining_job_names = Job.objects.filter(group=None)\
                                     .values('name').distinct()
    estimated = 0
    for name_dict in remaining_job_names:
        name = name_dict.get('name', None)
        executed_jobs = Job.objects.filter(name=name,
                                           executed__isnull=False,
                                           cancelled__isnull=True,
                                           group__isnull=True)
        remaining_jobs = Job.objects.filter(name=name,
                                            executed__isnull=True,
                                            cancelled__isnull=True,
                                            group__isnull=True,
                                            started__isnull=True)
        total_execution_time = 0
        for job in executed_jobs:
            delta = job.executed - job.started
            total_execution_time += float(delta.total_seconds())
        estimated += (total_execution_time / (executed_jobs.count() or 1)) \
                     * remaining_jobs.count()
    return estimated
