"""
    Implementation of the Slumber operations.
"""
from slumber.operations import ModelOperation, InstanceOperation
from slumber.server.http import require_user, require_permission

from django.shortcuts import Http404
from django.db.models import Count

from async import schedule
from async.models import Group
import datetime


# Method could be a function
# pylint: disable=R0201


class Schedule(ModelOperation):
    """Schedule a job via Slumber
    """
    def get(self, request, response, app, model):
        """Eventually this will return the parameters that are needed.
        """
        pass

    @require_permission('async.add_job')
    def post(self, request, response, _app, _model):
        """Wrap the API.
        """
        if hasattr(request.POST, 'getlist'):
            args = request.POST.getlist('args')
        else:
            args = request.POST.get('args', [])
        job = schedule(request.POST['name'],
            args=args,
            kwargs=request.POST.get('kwargs', {}),
            meta=request.POST.get('meta', {}),
            run_after=request.POST.get('run_after', None),
            priority=request.POST.get('priority', 5),
            group=request.POST.get('group', None)
            )
        response['job'] = dict(id=job.id)


class Progress(InstanceOperation):
    """Return information about the progress of a job.
    """
    @staticmethod
    def estimate_execution_duration(group):
        """Estimate of the total amount of time (in seconds) that the group
        will take to execute.
        """
        result = group.jobs.aggregate(
            job_count=Count('id'), executed_job_count=Count('executed'))
        total_jobs = result['job_count']
        total_executed_jobs = result['executed_job_count']
        if total_jobs > 0:
            # Don't allow to calculate if executed jobs are not valid.
            if total_executed_jobs == 0:
                return None, None, None
            if group.jobs.filter(executed__isnull=True):
                # Some jobs are unexecuted.
                time_consumed = datetime.datetime.now() - group.created
                estimated_time = datetime.timedelta(seconds=(
                    time_consumed.seconds/float(total_executed_jobs))
                        * total_jobs)
                remaining = estimated_time - time_consumed
            else:
                # All jobs in group are executed.
                estimated_time = (Progress.latest_executed_job_time(group)
                    - group.created)
                time_consumed = estimated_time
                remaining = datetime.timedelta(seconds=0)
            return estimated_time, remaining, time_consumed
        else:
            return None, None, None

    @staticmethod
    def latest_executed_job_time(group):
        """When the last executed job in the group was completed.
        """
        if not group.jobs.filter(executed__isnull=True):
            return group.jobs.latest('executed').executed

    @require_user
    def get(self, _request, response, _app, _models, group_reference_name):
        """The current progress and estimated completion time of the job.
        """
        groups = Group.objects.filter(reference=group_reference_name)
        if groups:
            latest_group = groups.latest('created')
            result = latest_group.jobs.aggregate(
                job_count=Count('id'), executed_job_count=Count('executed'))
            total_jobs = result['job_count']
            total_executed_jobs = result['executed_job_count']
            if total_jobs > 0:
                total_unexecuted_jobs = total_jobs - total_executed_jobs

                total, remaining, consumed = \
                    self.estimate_execution_duration(latest_group)
                latest = self.latest_executed_job_time(latest_group)
                response['progress'] = {
                    'id': latest_group.id,
                    'reference': latest_group.reference,
                    'created': latest_group.created.isoformat(),
                    'last_job_completed':
                        latest.isoformat() if latest else None,
                    'total_jobs': total_jobs,
                    'total_executed_jobs': total_executed_jobs,
                    'total_unexecuted_jobs': total_unexecuted_jobs,
                    'total_error_jobs':
                        latest_group.jobs.filter(errors__isnull=False)
                            .distinct().count(),
                    'estimated_total_time': total,
                    'consumed_seconds':
                        consumed.seconds if consumed else None,
                    'remaining_seconds':
                        remaining.seconds if remaining else None
                }
        else:
            raise Http404("Cannot find group with reference [%s]." %
                group_reference_name)

