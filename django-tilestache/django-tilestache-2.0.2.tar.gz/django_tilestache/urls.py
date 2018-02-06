# -*- coding: utf-8 -*-
from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from django_tilestache.viewsets import LayerViewSet
from django_tilestache.views import (
    TileStacheConfiguration,
    TileStacheTile,
)

router = DefaultRouter(trailing_slash=False)
router.register(r'layers', LayerViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(
        r'^api/tilestache/$',
        TileStacheConfiguration.as_view(),
        name='tilestache-configuration'
    ),
    url(
        r'^api/tilestache/(?P<layer_name>[-\w]+)/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+).(?P<extension>\w+)',
        TileStacheTile.as_view(),
        name='tilestache-tile'
    ),
]
