# -*- coding:utf-8 -*- 

from rest_framework import serializers, viewsets, mixins, decorators
from django.contrib.auth import models


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Group
        fields = ('url', 'name')


class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="get_full_name")
    permissions = serializers.ListField(source="get_all_permissions")
    class Meta:
        model = models.User
        fields = ('id', 'username', 'name', 'email', 'groups', 'permissions')


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, allow_blank=False, max_length=100)
    password = serializers.CharField(required=True, allow_blank=False, max_length=100)
