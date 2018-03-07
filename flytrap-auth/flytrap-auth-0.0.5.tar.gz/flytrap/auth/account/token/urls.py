#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from django.conf.urls import url
from django.conf import settings

from flytrap.auth.account.common.views import SignupView, UserInfo
from .views import ChangePasswordView, TokenLoginView

SHOW_SIGNUP = getattr(settings, 'SHOW_SIGNUP', True)

urlpatterns = [
    url('^change-password/$', ChangePasswordView.as_view({'post': 'create'})),
    url('^login/$', TokenLoginView.as_view({'post': 'create'})),
    url('^user_info/(?P<pk>\d+)/$', UserInfo.as_view({'get': 'retrieve'})),
]

if SHOW_SIGNUP:
    urlpatterns.append(url('^signup/$', SignupView.as_view({'post': 'create'})))
