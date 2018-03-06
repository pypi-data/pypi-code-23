# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from rest_framework.filters import SearchFilter

from django.db import models

class CustomSearchFilter(SearchFilter):
    def filter_queryset(self, request, queryset, view):
        # 全局搜索
        if request.query_params.get(self.search_param):
            return super(CustomSearchFilter, self).filter_queryset(request, queryset, view)

        # 按字段搜索
        else:
            search_params = getattr(view, 'search_params', [])

            for elem in search_params:
                for k,v in elem.items():
                    if request.query_params.get(k):
                        query = models.Q(**{v: request.query_params[k]})
                        queryset = queryset.filter(query)
            return queryset

class CustomSearchFilter1(SearchFilter):
    def filter_queryset(self, request, queryset, view):
        # 全局搜索
        if request.query_params.get(self.search_param):
            return super(CustomSearchFilter1, self).filter_queryset(request, queryset, view)

        # 按字段搜索
        else:
            search_params = getattr(view, 'search_params', [])

            for elem in search_params:
                for k,v in elem.items():
                    if request.query_params.get(k):
                        keyword = request.query_params[k]
                        if v.find('__in') > 0:
                            keyword = keyword.replace(' ', '').split(',')
                        query = models.Q(**{v: keyword})
                        queryset = queryset.filter(query)
            return queryset
