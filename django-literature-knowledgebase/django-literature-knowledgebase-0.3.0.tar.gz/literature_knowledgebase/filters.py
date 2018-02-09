# -*- coding: utf-8 -*-
from django.db.models import CharField

import django_filters
from genomix.filters import DisplayChoiceFilter

from . import choices, models


class ArticleFilter(django_filters.rest_framework.FilterSet):

    username = django_filters.CharFilter(
        name='user__username',
        lookup_expr='iexact',
    )
    source = DisplayChoiceFilter(choices=choices.SOURCES)

    class Meta:
        model = models.Article
        fields = [
            'source',
            'identifier',
            'user',
            'username',
            'active',
            'description',
        ]
        filter_overrides = {
            CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            }
        }
