# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from rest_framework import routers

from .views import StaticBlockView

app_name = 'static_blocks'

router = routers.DefaultRouter()
router.register('items', StaticBlockView)

urlpatterns = [
    url(r'^static_blocks/', include(routers.urls))
]
