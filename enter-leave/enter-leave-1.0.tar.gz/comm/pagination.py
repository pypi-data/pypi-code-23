# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.pagination import PageNumberPagination

class StandardPagination(PageNumberPagination):
    """
    The standard pagination settings for system.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        if request.query_params.get('page'):
            return super(StandardPagination, self).paginate_queryset(
                queryset, request, view)
        else:
            return None