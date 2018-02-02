
# coding: utf-8

from django.conf.urls import url, include
from .views import StaffViewSet
from rest_framework.routers import DefaultRouter
from .views import obtain_jwt_token, refresh_jwt_token, register_user

app_name ='jwt_auth'

router = DefaultRouter()
router.register(r'staff', StaffViewSet)

urlpatterns = [
    url(r'^api-auth/', obtain_jwt_token),
    url(r'^auth-token-refresh/', refresh_jwt_token),
    url(r'^api-register/', register_user),

    url(r'^', include(router.urls)),
]
