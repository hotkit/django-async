"""
    Django admin.
"""
from django.contrib import admin
from async.models import Error, Job


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
    list_display = ['__unicode__', 'scheduled', 'executed']
    inlines = [ErrorInline]


admin.site.register(Error)
admin.site.register(Job, JobAdmin)

