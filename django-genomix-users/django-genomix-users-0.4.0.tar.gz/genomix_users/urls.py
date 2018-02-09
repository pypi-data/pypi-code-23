# -*- coding: utf-8 -*-
from rest_framework import routers

from . import viewsets


router = routers.SimpleRouter()
router.register(r'', viewsets.UserViewSet)
router.register(r'profiles', viewsets.ProfileViewSet)

default_router = routers.DefaultRouter()
default_router.register(r'users', viewsets.UserViewSet)
default_router.register(r'user-profiles', viewsets.ProfileViewSet)

urlpatterns = default_router.urls
