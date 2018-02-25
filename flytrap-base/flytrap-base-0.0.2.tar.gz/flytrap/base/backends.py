# coding=utf-8
#
# Created by gaohuaguang
from django.utils import six
from django_filters import compat
from django_filters import filters
from django_filters.rest_framework import DjangoFilterBackend


class MongoDjangoFilterBackend(DjangoFilterBackend):
    def get_filter_class(self, view, queryset=None):
        """
        Return the django-filters `FilterSet` used to filter the queryset.
        """
        filter_class = getattr(view, 'filter_class', None)
        if filter_class:
            filter_model = filter_class.Meta.model

            assert issubclass(queryset._document, filter_model), \
                'FilterSet model %s does not match queryset model %s' % \
                (filter_model, queryset.model)

            return filter_class
        return

    def filter_queryset(self, request, queryset, view):
        filter_class = self.get_filter_class(view, queryset)

        if filter_class:
            return filter_class(request.query_params, queryset=queryset).qs

        return queryset


class MysqlDjangoFilterBackend(DjangoFilterBackend):
    def get_coreschema_field(self, field):
        enum = None
        if isinstance(field, filters.NumberFilter):
            field_cls = compat.coreschema.Number
        elif isinstance(field, filters.ChoiceFilter):
            field_cls = compat.coreschema.Enum
            enum = list(field.extra.get('choices'))
        else:
            field_cls = compat.coreschema.String
        description = six.text_type(field.extra.get('help_text', getattr(field, 'label', '')))
        if enum:
            return field_cls(description=description, enum=enum, default=enum[0][0])
        return field_cls(description=description)
