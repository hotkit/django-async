"""
    Django admin.
"""
from django.contrib import admin
from async.models import Error, Job, Group


class ErrorInline(admin.TabularInline):
    """Display the errors as part of the Job screen.
    """
    model = Error
    fields = ['traceback']
    readonly_fields = ['traceback']
    max_num = 0


def display_group(obj):
    return obj.group.reference if obj.group else None

display_group.short_description = 'Group'


class JobAdmin(admin.ModelAdmin):
    """Allow us to manipulate jobs.
    """

    list_display = ['__unicode__', 'scheduled', 'executed', display_group]
    inlines = [ErrorInline]


class GroupAdmin(admin.ModelAdmin):
    """Allow us to see groups.
    """

    def executed_jobs(obj):
        return obj.jobs.filter(executed__isnull=False).count()
    executed_jobs.short_description = 'Executed'

    def unexecuted_jobs(obj):
        return obj.jobs.filter(executed__isnull=True).count()
    unexecuted_jobs.short_description = 'Unexecuted'

    list_display = ['__unicode__', 'description', executed_jobs, unexecuted_jobs]

admin.site.register(Error)
admin.site.register(Job, JobAdmin)
admin.site.register(Group, GroupAdmin)

