#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from django.contrib.auth import get_user_model, authenticate
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from flytrap.auth.account.common.serizliers import ChangePasswordSerializer, UserSerializer, UserLoginSerializer

User = get_user_model()


class ChangePasswordView(ModelViewSet):
    serializer_class = ChangePasswordSerializer
    authentication_classes = (TokenAuthentication,)

    def update(self, request, *args, **kwargs):
        """
        修改密码
        """
        user = User.objects.get(username=request.user)
        if user.check_password(request.data['old_password']):
            user.set_password(request.data['new_password'])
            user.save()
            return Response(UserSerializer(user).data)
        else:
            return Response({'status': 'error'})


class TokenLoginView(ModelViewSet):
    serializer_class = UserLoginSerializer
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def create(self, request, *args, **kwargs):
        """
        用户token方式登录
         """
        user = authenticate(username=request.data['username'], password=request.data['password'])
        if user and user.is_active:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'status': 'ok'})
        else:
            return Response({'status': 'error', 'message': 'not permission'})
