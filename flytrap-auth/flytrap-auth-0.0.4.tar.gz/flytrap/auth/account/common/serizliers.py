#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    用户信息
    """

    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class UserSignupSerializer(serializers.ModelSerializer):
    """
    用户注册
    """

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'password'
        )

        extra_kwargs = {
            'password': {'write_only': True},
        }


class UserLoginSerializer(serializers.ModelSerializer):
    """
    登录
    """

    class Meta:
        model = User
        fields = (
            'username',
            'password'
        )


class ChangePasswordSerializer(serializers.ModelSerializer):
    """
    改密
    """
    old_password = serializers.CharField(label='旧密码')
    new_password = serializers.CharField(source='password', label='新密码')

    class Meta:
        model = User
        fields = ('old_password', 'new_password')
