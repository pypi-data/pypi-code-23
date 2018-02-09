# -*- coding: utf-8 -*-
from rest_framework import routers

from . import viewsets


router = routers.SimpleRouter()
router.register(r'', viewsets.ArticleViewSet)

default_router = routers.DefaultRouter()
default_router.register(r'articles', viewsets.ArticleViewSet)


urlpatterns = default_router.urls
