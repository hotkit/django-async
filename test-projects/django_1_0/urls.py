from django.conf.urls.defaults import *
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    # Enable Slumber
    (r'^slumber/', include('slumber.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),
)
