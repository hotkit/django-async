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
    from django.utils import timezone
except ImportError: # pragma: no cover
    # pylint: disable = ungrouped-imports
    from datetime import datetime as timezone

from async.models import Error, Job, Group
from async.utils import full_name
from async.stats import estimate_current_job_completion, \
    estimate_rough_queue_completion


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
        if isinstance(group, Group):
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
    try:
        mark_cancelled = Job.objects.filter(executed=None,
            identity=sha1(unicode(job)).hexdigest())
    except NameError:
        mark_cancelled = Job.objects.filter(executed=None,
            identity=sha1(str(job).encode('utf-8')).hexdigest())
    mark_cancelled.update(cancelled=_get_now())


def health(estimation_fn=estimate_rough_queue_completion):
    """Return information about the health of the queue in a format that
    can be turned into JSON.
    """
    # Import this here so that we only need slumber if health is called.
    try:
        from slumber import data_link
    except ImportError:  # pragma: no cover
        return {}
    output = {'queue': {}, 'errors': {}}

    output['queue']['all-jobs'] = Job.objects.all().count()

    output['queue']['executed'] = Job.objects.exclude(executed=None).count()
    output['queue']['executed-details'] = \
        get_grouped_aggregate(jobs_type='executed')
    output['queue']['oldest-executed'] = data_link(get_first(
        Job.objects.exclude(executed=None).order_by('executed')))
    output['queue']['most-recent-executed'] = data_link(get_first(
        Job.objects.exclude(executed=None).order_by('-executed')))

    output['queue']['remaining'] = Job.objects.filter(
        executed=None, cancelled=None).count()
    # output['queue']['remaining-details'] = \
    #     get_grouped_aggregate(
    #         jobs_type='done',
    #         complement=True)

    output['queue']['not-executed'] = \
        Job.objects.filter(executed=None, cancelled__isnull=True).count()
    output['queue']['not-executed-details'] = \
        get_not_exeuted_details()

    output['queue']['cancelled'] = \
        Job.objects.filter(cancelled__isnull=False).count()
    output['queue']['oldest-cancelled'] = data_link(get_first(
        Job.objects.exclude(cancelled=None).order_by('cancelled')))
    output['queue']['most-recent-cancelled'] = data_link(get_first(
        Job.objects.exclude(cancelled=None).order_by('-cancelled')))
    output['queue']['cancelled-details'] = \
        get_grouped_aggregate(jobs_type='cancelled', complement=True)

    output['queue']['estimated-completion-current-job'] = \
        estimate_current_job_completion()
    output['queue']['estimated-completion'] = estimation_fn()

    output['errors']['number'] = Error.objects.all().count()
    return output


def get_not_exeuted_details():
    """
       Returns count of not executed jobs, grouped by name, based on
       job type.
    """
    from django.db.models import Count
    values = Job.objects.values('name')
    result = list(values.filter(Q(executed=None) &
                                Q(cancelled__isnull=True))
                  .order_by('name').annotate(Count('name')))
    return dict([(v['name'], dict(count=v['name__count'])) for v in result])


def get_grouped_aggregate(jobs_type, complement=False):
    """
       Returns count of jobs, grouped by name, based on
       job type.
    """
    # Have this import here so we can use most things on Django 1.0
    from django.db.models import Count
    values = Job.objects.values('name')
    if complement:
        result = list(values.filter(**{jobs_type: None})\
                     .order_by('name').annotate(Count('name')))
    else:
        result = list(values.exclude(**{jobs_type: None})\
                 .order_by('name').annotate(Count('name')))
    return dict([(v['name'], dict(count=v['name__count'])) for v in result])


def get_first(queryset, default=None):
    """ Return first element of queryset or default """
    if queryset:
        return queryset[0]
    return default


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
