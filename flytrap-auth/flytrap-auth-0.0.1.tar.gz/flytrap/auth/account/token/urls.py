#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from django.conf.urls import url

from flytrap.auth.account.common.views import SignupView
from .views import ChangePasswordView, TokenLoginView

urlpatterns = [
    url('^signup/$', SignupView.as_view({'post': 'create'})),
    url('^change-password/$', ChangePasswordView.as_view({'post': 'create'})),
    url('^login/$', TokenLoginView.as_view({'post': 'create'})),
]
