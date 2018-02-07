# -*- coding: utf-8 -*-
# emailauth APP URLs

from django.conf.urls import *
from emailuser.views import login_view, logout_view, auth

urlpatterns = [
    url(r'login/', login_view, name='login'),
    url(r'logout/', logout_view, name='logout'),
    url(r'auth/(?P<user_id>\d+)/(?P<token>\w+)/', auth, name='auth'),
]
