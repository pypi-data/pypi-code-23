from __future__ import absolute_import, print_function, unicode_literals

from django.conf.urls import url
from dbfilestorage import views

urlpatterns = [
    url(r'^(?P<name>.*)$', views.show_file, name="dbstorage_file"),
]
