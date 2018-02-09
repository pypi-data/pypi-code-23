# -*- coding: utf-8
from django.contrib.auth import get_user_model
from django.db.models import CharField

import django_filters

from . import models


class UserFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = get_user_model()
        fields = [
            'username',
        ]
        filter_overrides = {
            CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'iexact',
                },
            },
        }


class ProfileFilter(django_filters.rest_framework.FilterSet):

    username = django_filters.CharFilter(
        name='user__username',
        lookup_expr='iexact',
    )

    class Meta:
        model = models.Profile
        fields = [
            'user',
            'user__username',
            'title',
        ]
        filter_overrides = {
            CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
        }
