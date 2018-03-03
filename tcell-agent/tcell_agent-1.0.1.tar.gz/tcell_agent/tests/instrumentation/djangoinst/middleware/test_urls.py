# this is used by other middleware tests to set settings.ROOT_URLCONF

from django.conf.urls import include, url  # noqa
from django.contrib import admin  # noqa

urlpatterns = []

from django.contrib.staticfiles.urls import staticfiles_urlpatterns  # noqa
