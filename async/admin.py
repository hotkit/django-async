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


class JobAdmin(admin.ModelAdmin):
    """Allow us to manipulate jobs.
    """

    def display_group(obj):
        return u'%s' % obj.group.reference
    display_group.short_description = 'Group'

    list_display = ['__unicode__', 'scheduled', 'executed', display_group]
    inlines = [ErrorInline]


class GroupAdmin(admin.ModelAdmin):
    """Allow us to see groups.
    """
    list_display = ['__unicode__']

admin.site.register(Error)
admin.site.register(Job, JobAdmin)
admin.site.register(Group, GroupAdmin)

