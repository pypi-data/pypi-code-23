#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from . import api_views

urlpatterns = [
    url(r'^api/device-mobility/$', api_views.DeviceMobilityListView.as_view()),
    url(r'^api/device-mobility/(?P<pk>[0-9]+)/$', api_views.DeviceMobilityDetailView.as_view()),
    url(r'^api/device/$', api_views.DeviceListView.as_view()),
    url(r'^api/device/(?P<pk>[0-9]+)/$', api_views.DeviceDetailView.as_view()),
]
