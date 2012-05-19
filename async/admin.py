"""
    Django admin.
"""
from django.contrib import admin
from async.models import Error, Job


admin.site.register(Error)
admin.site.register(Job)

