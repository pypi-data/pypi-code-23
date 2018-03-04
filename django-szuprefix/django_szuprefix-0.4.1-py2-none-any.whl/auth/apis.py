# -*- coding:utf-8 -*-

from . import serializers
from rest_framework import viewsets, decorators, response, status
from django_szuprefix.api import register
from django.contrib.auth import authenticate, login as auth_login


class UserViewSet(viewsets.GenericViewSet):
    serializer_class = serializers.UserSerializer

    def get_object(self):
        return self.request.user

    @decorators.list_route(['post'], authentication_classes=[], permission_classes=[])
    def login(self, request, *args, **kwargs):
        serializer = serializers.LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(**serializer.validated_data)
            if user:
                auth_login(request, user)
                return response.Response(self.get_serializer(user).data)
        return response.Response(serializer.errors, status=400)

    @decorators.list_route(['get'])
    def current(self, request):
        serializer = self.get_serializer(request.user, context={'request': request})
        return response.Response(serializer.data)

    @decorators.list_route(['post'], authentication_classes=[], permission_classes=[])
    def logout(self, request):
        from django.contrib.auth import logout
        logout(request)
        return response.Response(status=status.HTTP_200_OK)

register('auth', 'user', UserViewSet, base_name='user')
