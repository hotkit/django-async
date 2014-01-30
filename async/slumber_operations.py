"""
    Implementation of the Slumber operations.
"""
from slumber.operations import ModelOperation, InstanceOperation
from slumber.server.http import require_permission

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

    def calculate_estimated_time_finishing(self, group):
        total_jobs = group.jobs.count()
        if total_jobs:
            total_executed_jobs = group.jobs.filter(executed__isnull=False).count()
            # Don't allow to calculate if executed jobs are not valid.
            if total_executed_jobs == 0: return None
            if group.jobs.filter(executed__isnull=True):
                # Some jobs are unexecuted.
                time_consumed = datetime.datetime.today() - group.created
                estimated_time = (time_consumed.seconds/float(total_executed_jobs)) * total_jobs
            else:
                # All jobs in group are executed.
                estimated_time = (self.last_job_was_executed_was_executed(group) - group.created).seconds
            return datetime.timedelta(seconds=estimated_time)
        else:
            return None

    def last_job_was_executed_was_executed(self, group):
        if not group.jobs.filter(executed__isnull=True):
            return group.jobs.latest('executed').executed

    def get(self, request, response, app, models, group_reference_name):
        groups = Group.objects.filter(reference=group_reference_name)
        if groups:
            latest_group = groups.latest('created')
            total_jobs = latest_group.jobs.count()
            if total_jobs > 0:
                total_executed_jobs = latest_group.jobs.filter(executed__isnull=False).count()
                total_unexecuted_jobs = total_jobs - total_executed_jobs

                response['progress'] = {
                    'id': latest_group.id,
                    'reference': latest_group.reference,
                    'created': latest_group.created,
                    'last_job_completed': self.last_job_was_executed_was_executed(latest_group),
                    'total_jobs': total_jobs,
                    'total_executed_jobs': total_executed_jobs,
                    'total_unexecuted_jobs': total_unexecuted_jobs,
                    'total_error_jobs': latest_group.jobs.filter(errors__isnull=False).count(),
                    'estimated_time_finishing': self.calculate_estimated_time_finishing(latest_group)
                }




