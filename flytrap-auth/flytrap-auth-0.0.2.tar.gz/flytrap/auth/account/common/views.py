#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from django.contrib.auth import hashers
from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from flytrap.auth.account.common.serizliers import UserSignupSerializer


class SignupView(ModelViewSet):
    serializer_class = UserSignupSerializer
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def create(self, request, *args, **kwargs):
        """
        用户注册
        """
        request.data['password'] = hashers.make_password(request.data['password'])
        return super(SignupView, self).create(request, *args, **kwargs)
