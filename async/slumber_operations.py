"""
    Implementation of the Slumber operations.
"""
from slumber.operations import ModelOperation, InstanceOperation
from slumber.server.http import require_permission

from django.shortcuts import Http404
from django.db.models import Count

from async import schedule
from async.models import Group, Job
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
            priority=request.POST.get('priority', 5))
        response['job'] = dict(id=job.id)


class Progress(InstanceOperation):

    @staticmethod
    def calculate_estimated_time_finishing(group):
        result = group.jobs.aggregate(job_count=Count('id'), executed_job_count=Count('executed'))
        total_jobs = result['job_count']
        total_executed_jobs = result['executed_job_count']
        if total_jobs > 0:
            # Don't allow to calculate if executed jobs are not valid.
            if total_executed_jobs == 0: return None
            if group.jobs.filter(executed__isnull=True):
                # Some jobs are unexecuted.
                time_consumed = datetime.datetime.today() - group.created
                estimated_time = (time_consumed.seconds/float(total_executed_jobs)) * total_jobs
            else:
                # All jobs in group are executed.
                estimated_time = (Progress.last_job_was_executed_was_executed(group) - group.created).seconds
            return datetime.timedelta(seconds=estimated_time)
        else:
            return None

    @staticmethod
    def last_job_was_executed_was_executed(group):
        if not group.jobs.filter(executed__isnull=True):
            return group.jobs.latest('executed').executed

    def get(self, request, response, app, models, group_reference_name):
        groups = Group.objects.filter(reference=group_reference_name)
        if groups:
            latest_group = groups.latest('created')
            print latest_group
            result = latest_group.jobs.aggregate(job_count=Count('id'), executed_job_count=Count('executed'))
            total_jobs = result['job_count']
            total_executed_jobs = result['executed_job_count']
            if total_jobs > 0:
                total_unexecuted_jobs = total_jobs - total_executed_jobs

                response['progress'] = {
                    'id': latest_group.id,
                    'reference': latest_group.reference,
                    'created': latest_group.created,
                    'last_job_completed': Progress.last_job_was_executed_was_executed(latest_group),
                    'total_jobs': total_jobs,
                    'total_executed_jobs': total_executed_jobs,
                    'total_unexecuted_jobs': total_unexecuted_jobs,
                    'total_error_jobs': latest_group.jobs.filter(errors__isnull=False).distinct().count(),
                    'estimated_time_finishing': Progress.calculate_estimated_time_finishing(latest_group)
                }
        else:
            raise Http404("Cannot find group with reference [%s]." % group_reference_name)



