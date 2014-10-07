"""
    Schedule the execution of an async task.
"""
from datetime import timedelta
# No name 'sha1' in module 'hashlib'
# pylint: disable=E0611
from hashlib import sha1
from simplejson import dumps

from django.db.models import Q
try:
    # No name 'timezone' in module 'django.utils'
    # pylint: disable=E0611
    from django.utils import timezone
except ImportError: # pragma: no cover
    from datetime import datetime as timezone

from async.models import Error, Job, Group
from async.utils import full_name


def _get_now():
    """Get today datetime, testing purpose.
    """
    return timezone.now()


def schedule(function, args=None, kwargs=None,
        priority=5, run_after=None, group=None, meta=None):
    """Schedule a tast for execution.
    """
    # Too many arguments
    # pylint: disable=R0913
    if group:
        if type(group) == Group:
            expected_group = group
        else:
            expected_group = Group.latest_group_by_reference(group)
    else:
        expected_group = None
    job = Job(
        name=full_name(function),
            args=dumps(args or []), kwargs=dumps(kwargs or {}),
        meta=dumps(meta or {}), scheduled=run_after,
        priority=priority,
        group=expected_group)
    job.save()
    return job


def deschedule(function, args=None, kwargs=None):
    """Remove any instances of the job from the queue.
    """
    job = Job(
        name=full_name(function),
            args=dumps(args or []), kwargs=dumps(kwargs or {}))
    mark_cancelled = Job.objects.filter(executed=None,
        identity=sha1(unicode(job)).hexdigest())
    mark_cancelled.update(cancelled=_get_now())


def health():
    """Return information about the health of the queue in a format that
    can be turned into JSON.
    """
    output = {'queue': {}, 'errors': {}}

    output['queue']['all-jobs'] = Job.objects.all().count()

    output['queue']['not-executed'] = Job.objects.filter(executed=None).count()
    output['queue']['executed'] = Job.objects.exclude(executed=None).count()
    output['queue']['oldest-executed'] = get_first(
        Job.objects.exclude(executed=None).order_by('executed'))
    output['queue']['most-recent-executed'] = get_first(
        Job.objects.exclude(executed=None).order_by('-executed'))

    output['queue']['cancelled'] = Job.objects.filter(cancelled=None).count()
    output['queue']['oldest-cancelled'] = get_first(
        Job.objects.exclude(cancelled=None).order_by('cancelled'))
    output['queue']['most-recent-cancelled'] = get_first(
        Job.objects.exclude(cancelled=None).order_by('-cancelled'))

    output['queue']['estimated-completion-current-job'] = _estimate_current_completion()
    output['queue']['estimated-completion'] = _estimate_completion_all()

    output['errors']['number'] = Error.objects.all().count()
    output['errors']['oldest-error'] = get_first(
        Error.objects.all().order_by('executed'))
    output['errors']['most-recent-error'] = get_first(
        Error.objects.all().order_by('-executed'))
    return output


def get_first(queryset, default=None):
    """ Return first element of queryset or default """
    if queryset:
        return queryset[0]
    return default


def _estimate_current_completion():
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
        return None


def _estimate_completion_all():
    """Estimate average time (in seconds) that the queue
       will take to execute

       Return floating point value indicating average time
       for completion of all jobs in the queue
    """
    total_estimated = 0
    for group in Group.objects.all():
        estimated, _, _ = group.estimate_execution_duration()
        if isinstance(estimated, timedelta):
            total_estimated += estimated.total_seconds()
    return round(total_estimated +
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
                                            group__isnull=True)
        total_execution_time = 0
        for job in executed_jobs:
            delta = job.executed - job.started
            total_execution_time += float(delta.total_seconds())
        estimated += (total_execution_time / (executed_jobs.count() or 1)) \
                     * remaining_jobs.count()
    return estimated


def remove_old_jobs(remove_jobs_before_days=30, resched_hours=8):
    """Remove old jobs start from these conditions

    Removal date for jobs is `remove_jobs_before_days` days earlier
    than when this is executed.

    It will delete jobs and groups that meet the following:
    - Jobs execute before the removal date and which are not in any group.
    - Groups (and their jobs) where all jobs have executed before the removal
        date.
    """
    start_remove_jobs_before_dt = _get_now() - timedelta(
        days=remove_jobs_before_days)

    # Jobs not in a group that are old enough to delete
    rm_job = (Q(executed__isnull=False) &
        Q(executed__lt=start_remove_jobs_before_dt)) | \
             (Q(cancelled__isnull=False) &
        Q(cancelled__lt=start_remove_jobs_before_dt))
    Job.objects.filter(Q(group__isnull=True), rm_job).delete()

    # Groups with all executed jobs -- look for groups that qualify
    groups = Group.objects.filter(Q(jobs__executed__isnull=False) |
                                  Q(jobs__cancelled__isnull=False))
    for group in groups.iterator():
        if group.jobs.filter(rm_job).count() == group.jobs.all().count():
            group.jobs.filter(rm_job).delete()
            group.delete()

    next_exec = _get_now() + timedelta(hours=resched_hours)

    schedule(remove_old_jobs,
        args=[remove_jobs_before_days, resched_hours],
        run_after=next_exec)
