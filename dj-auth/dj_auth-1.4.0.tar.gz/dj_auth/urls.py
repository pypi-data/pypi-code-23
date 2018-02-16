# -*- coding: utf-8 -*-
from django.conf.urls import url

from .views import ObjectFilterValuesWidgetView

urlpatterns = [url(r'^loadvalues/(?P<content_type_id>[0-9]+)/$', ObjectFilterValuesWidgetView, name='loadvalues'), ]
