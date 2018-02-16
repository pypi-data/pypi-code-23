# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse

from .models import ObjectFilter
from .widgets import ObjectFilterValuesWidget


class ObjectFilterListMixin(object):

    def get_queryset(self):
        queryset = super(ObjectFilterListMixin, self).get_queryset()

        if hasattr(self.request, 'user') and self.request.user.is_authenticated:
            user = self.request.user
        else:
            user = None

        filter_query, exclude_query = ObjectFilter.build_filter(user=user, content_type=ContentType.objects.get_for_model(self.model), session=self.request.session)

        if exclude_query:
            queryset = queryset.exclude(exclude_query).distinct()
        if filter_query:
            queryset = queryset.filter(filter_query).distinct()
        return queryset


class _ObjectFilterDetailMixin(object):
    def get_object(self):
        obj = super(_ObjectFilterDetailMixin, self).get_object()

        if hasattr(self.request, 'user') and self.request.user.is_authenticated:
            user = self.request.user
        else:
            user = None

        filter_query, exclude_query = ObjectFilter.build_filter(user=user, content_type=ContentType.objects.get_for_model(self.model), session=self.request.session)

        if exclude_query:
            if self.model.objects.exclude(exclude_query).filter(pk=obj.id).exists():
                return obj
            else:
                raise PermissionDenied
        if filter_query:
            if self.model.objects.filter(filter_query).filter(pk=obj.id).exists():
                return obj
            else:
                raise PermissionDenied

        return obj


class ObjectFilterDetailMixin(_ObjectFilterDetailMixin):
    pass


class ObjectFilterUpdateMixin(_ObjectFilterDetailMixin):
    pass


class ObjectFilterDeleteMixin(_ObjectFilterDetailMixin):
    pass


def ObjectFilterValuesWidgetView(request, content_type_id=None, field_name=None, values=None):
    widget = ObjectFilterValuesWidget(attrs={'content_type': content_type_id, 'field_name': field_name, 'values': values})
    return HttpResponse(widget.render(field_name, [], ))
