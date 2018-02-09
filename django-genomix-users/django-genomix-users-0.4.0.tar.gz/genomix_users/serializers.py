# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator

from rest_framework import serializers

from . import models


class UserSerializer(serializers.ModelSerializer):
    """Serializer for Users."""

    class Meta:
        model = get_user_model()
        fields = (
            'id', 'username', 'email',
            'first_name', 'last_name',
            'is_staff', 'is_active', 'is_superuser',
            'last_login', 'date_joined',
        )
        # NOTE: This is to make it accessible to ProfileSerializer
        extra_kwargs = {
            'username': {
                'validators': [UnicodeUsernameValidator()],
            }
        }


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for User Profiles."""
    user = UserSerializer()

    class Meta:
        model = models.Profile
        fields = (
            'id', 'user', 'title',
            'created', 'modified',
        )

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        username = user_data.get('username')

        instance.user = get_user_model().objects.get(username=username)
        instance.title = validated_data.get('title')
        instance.save()
        return instance
