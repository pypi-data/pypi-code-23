from django.conf.urls import include, url
from django.contrib import admin
from django import VERSION as DJANGO_VERSION

from filebrowser.sites import site

admin.autodiscover()

if DJANGO_VERSION >= (1, 9):
    urlpatterns = [
        url(r'^admin/filebrowser/', include(site.urls[:2], namespace=site.urls[2])),
        url(r'^admin/', include(admin.site.urls[:2], namespace=admin.site.urls[2])),
    ]
else:
    urlpatterns = [
        url(r'^admin/filebrowser/', include(site.urls)),
        url(r'^admin/', include(admin.site.urls)),
    ]
