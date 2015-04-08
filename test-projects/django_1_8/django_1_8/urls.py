from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'django_1_8.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # Enable Slumber
    (r'^slumber/', include('slumber.urls')),

    url(r'^admin/', include(admin.site.urls)),
]
