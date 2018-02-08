


import datetime

from django.core.cache import cache
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status

from octo_drf.caching.helpers import set_cache_headers


class CacheViewSetMixin:
    """
    Миксин перегружает методы list и retrieve, добавляя возможно кешировать сериализованные данные
    Для работы нужен redis, чтобы хранить сериализованный ответ и дату последнего изменения.
    Так же для поддержки кеширования на веб сервере, нужно настроить nginx
    Чтобы кеш инвалидорался автоматически нужно заполнить CACHE_MAP в файле map.py

    Last-Modified выставляется исходя из последнего изменения данных, автоматически
    Cache-Controls=max-age - выставляется с помощью атрибута max_age. Принимает время в секундах

    Данные в redis хранятся ввиде {cache_key: [дата_изменения, serializer.data]
    """

    max_age = None

    @classmethod
    def get_cache_key(cls):
        """
        Вовзращает уникальный ключ для redis, использует в CACHE_MAP
        """
        return '{}.{}'.format(cls.__module__, cls.__name__)

    def _get_cache_key(self, lookup_field=None):
        """
        Возвращает дефолтный ключ из одноименного клас метода, для хранения списка сериализованных объектов
        Если предоставлен lookup_field, создает новый уникальный ключ для сериализованного объекта в retrieve методе
        """
        key = self.__class__.get_cache_key()
        if lookup_field:
            key += ':{}'.format(lookup_field)
        return key

    def _get_data_from_cache(self, cache_key):
        """
        Функция проверяет актуальность данных в redis и возвращает 304, если данные актуальны
        Если данные не актуальны отдает их из redis, вместе с заголовками кеша
        Если данных нет в кеше, возвращает None
        """
        cached_data = cache.get(cache_key)
        if not cached_data:
            return None
        modified_since = self.request.META.get('HTTP_IF_MODIFIED_SINCE')
        last_modified = cached_data[0]
        data = cached_data[1]

        if cached_data and modified_since:
            modified_since = datetime.datetime.strptime(modified_since, '%Y-%m-%d %H:%M:%S.%f')
            if last_modified > modified_since:
                return Response(data, headers=set_cache_headers(last_modified, self.max_age))
            return Response(status=status.HTTP_304_NOT_MODIFIED)
        else:
            return Response(data, headers=set_cache_headers(last_modified, self.max_age))

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        cache_key = self._get_cache_key()
        response = self._get_data_from_cache(cache_key)
        if response:
            return response

        serializer = self.get_serializer(queryset, many=True)
        now = datetime.datetime.now()
        cache.set(cache_key, [now, serializer.data])
        return Response(serializer.data, headers=set_cache_headers(now, self.max_age))

    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        cache_key = self._get_cache_key(lookup_url_kwarg)
        response = self._get_data_from_cache(cache_key)
        if response:
            return response

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        instance = get_object_or_404(queryset, **filter_kwargs)
        serializer = self.get_serializer(instance)
        now = datetime.datetime.now()
        cache.set(cache_key, [now, serializer.data])
        return Response(serializer.data, headers=set_cache_headers(now, self.max_age))
