#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from django.contrib.auth import hashers
from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from flytrap.auth.account.common.serizliers import UserSignupSerializer, UserSerializer


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


class UserInfo(ModelViewSet):
    serializer_class = UserSerializer
    authentication_classes = (permissions.IsAuthenticated,)

    def retrieve(self, request, *args, **kwargs):
        """获取当前用户信息"""
        return super(UserInfo, self).retrieve(request, *args, **kwargs)

    def get_object(self):
        self.kwargs['pk'] = self.request.user.id
        return super(UserInfo, self).get_object()
