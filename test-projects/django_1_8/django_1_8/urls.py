from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Enable Slumber
    url(r'^slumber/', include('slumber.urls')),

    url(r'^admin/', include(admin.site.urls)),
]
