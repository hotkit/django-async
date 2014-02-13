"""
    Schedule the execution of an async task.
"""
from datetime import datetime, timedelta
# No name 'sha1' in module 'hashlib'
# pylint: disable=E0611
from hashlib import sha1
from simplejson import dumps

from async.models import Error, Job, Group
from async.utils import full_name
from django.db.models import Q


def schedule(function, args=None, kwargs=None,
        priority=5, run_after=None, group=None, meta=None):
    """Schedule a tast for execution.
    """
    # Too many arguments
    # pylint: disable=R0913
    if group:
        expected_group = Group.objects.filter(reference=group).latest('created')
    else:
        expected_group = None
    job = Job(
        name=full_name(function),
            args=dumps(args or []), kwargs=dumps(kwargs or {}),
        meta=dumps(meta or {}), scheduled=run_after,
        priority=priority,
        group=expected_group
        )
    job.save()
    return job


def deschedule(function, args=None, kwargs=None):
    """Remove any instances of the job from the queue.
    """
    job = Job(
        name=full_name(function),
            args=dumps(args or []), kwargs=dumps(kwargs or {}))
    mark_executed = Job.objects.filter(executed=None,
        identity=sha1(unicode(job)).hexdigest())
    mark_executed.update(executed=datetime.now())


def health():
    """Return information about the health of the queue in a format that
    can be turned into JSON.
    """
    output = {'queue': {}, 'errors': {}}
    output['queue']['all-jobs'] = Job.objects.all().count()
    output['queue']['not-executed'] = Job.objects.filter(executed=None).count()
    output['queue']['executed'] = Job.objects.exclude(executed=None).count()
    output['errors']['number'] = Error.objects.all().count()
    return output


def get_today_dt():
    """Get today datetime, testing purpose.
    """
    return datetime.today()


def remove_old_jobs(remove_jobs_before_days=None):
    """Remove old jobs start from these conditions
    - Job executed dt is elder that remove_jobs_before_days and
      it is not in any group.
    - Job executed dt is elder that start_date and
      is in group that all jobs (in that group) are executed.
    """
    if remove_jobs_before_days is None or not remove_jobs_before_days:
        remove_jobs_before_days = 30

    start_remove_jobs_before_dt = get_today_dt() - timedelta(
        days=remove_jobs_before_days)

    # jobs_does_not_belong_to_any_group = Q(group__isnull=True)
    # jobs_all_executed_in_group = Q(group__jobs__executed__isnull=False)
    # conditions = jobs_does_not_belong_to_any_group | jobs_all_executed_in_group
    #
    # jobs_executed_before_this_day = Q(
    #     executed__lt=start_remove_jobs_before_dt)
    # jobs_must_complete = Q(executed__isnull=False)
    #
    # Job.objects.filter(
    #     conditions,
    #     jobs_must_complete,
    #     jobs_executed_before_this_day
    # ).delete()
    Job.objects.filter(
        Q(group__isnull=True) | Q(group__jobs__executed__isnull=False),
        Q(executed__isnull=False),
        Q(executed__lt=start_remove_jobs_before_dt)
    ).delete()

    def get_next_round():
        """Get new schedule time.
        """
        return get_today_dt() + timedelta(hours=8)

    schedule('async.api.remove_old_jobs', args=[remove_jobs_before_days],
             run_after=get_next_round())
