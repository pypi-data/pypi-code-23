# -*- coding: utf-8 -*-
from django.db.models import CharField, TextField

import django_filters
from genomix.filters import DisplayChoiceFilter

from . import choices, models


class FileFilter(django_filters.rest_framework.FilterSet):

    type = DisplayChoiceFilter(choices=choices.FILE_TYPES)

    class Meta:
        model = models.File
        fields = [
            'name',
            'description',
            'url',
            'path',
            'active',
            'type',
            'active',
            'relative_path',
        ]
        filter_overrides = {
            CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
            TextField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            }
        }
