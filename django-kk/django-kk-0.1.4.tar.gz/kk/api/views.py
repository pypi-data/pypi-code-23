import re
import datetime
import time
import urllib
import json

from inspect import ismethod

from django.views import generic
from django.utils import timezone
from django.utils.decorators import classonlymethod
from django.db.models import (
    Model, Manager, AutoField, CharField
)
from django.db.models.query import QuerySet
from django.db.models.fields.files import ImageFieldFile
from django.core.exceptions import FieldDoesNotExist
from django.http import (HttpResponse,
    HttpResponseNotFound, HttpResponseForbidden)

from .. import utils

DEFAULT_PAGE_SIZE = 200
DEFAULT_PAGE_SIZE_MAX = 200

class Stream:
    user = None
    query = None
    params = None # from path

    count = None
    skip = None

    keys = [
        ('count', int, DEFAULT_PAGE_SIZE),
        ('skip', int, 0)
    ]

    def __init__(self, HttpRequest, params):
        self.user = HttpRequest.user
        self.query = HttpRequest.GET
        self.params = params
        self.client_params = {}

        for key, type, default in self.keys:
            value = HttpRequest.GET.get(key, default)
            self.client_params[key] = type(value)


def convert_to_json(method):
    def wrapper(self, HttpRequest, **kwargs):
        stream = method(self, HttpRequest, **kwargs)

        if isinstance(stream.data, HttpResponse):
            return stream.data

        if stream.data == None:
            return HttpResponseNotFound()

        response = HttpResponse(
            json.dumps(
                stream.data,
                ensure_ascii = False,
                sort_keys = True
            ),
            content_type = 'application/json'
        )

        if hasattr(stream, 'total'):
            response['Total'] = stream.total

        if hasattr(stream, 'skip'):
            response['Skip'] = stream.skip

        if hasattr(stream, 'count'):
            response['Count'] = stream.count

#        print(stream)

        return response

    return wrapper


class BaseAPI(generic.View):
    model = None
    key = 'id'
#    data = None

    page_size = DEFAULT_PAGE_SIZE
    page_size_max = DEFAULT_PAGE_SIZE_MAX

    @classonlymethod
    def as_api(self, **kwargs):
        self.dynamic_filters = {};
        if len(kwargs) > 0:
            if 'filters' in kwargs:
                # Представление получает новые фильтры из urls.py (.as_api())
                filters = kwargs['filters']
                for key in filters:
#                    print('> > >', key)
                    value = filters[key]
                    if type(value) == tuple and len(value) == 2:
                        self.dynamic_filters.update({
                            key: value
                        })
        return self.as_view()

    available_filters = []
    dynamic_filters = {}
    def get_filters(self, stream):
        filters = {
            'status': True,
        }

        #stream.user.is_staff or stream.user.is_superuser
        try:
            field = self.model._meta.get_field('pub_date')
            filters.update({
                'pub_date__lt': timezone.now()
            })
        except FieldDoesNotExist:
            pass

        if len(self.dynamic_filters) > 0:
#            print('... dynamic_filters:', self.dynamic_filters)
            for key in self.dynamic_filters:
                param_key = self.dynamic_filters[key][0]
                param_class = self.dynamic_filters[key][1]

#                print('param_key', param_key)
#                print('param_class', param_class)

                if param_key in stream.params:
                    value = param_class(stream.params[param_key])
                    filters[key] = value

#        for filter in self.available_filters:
#            if (stream.query.__contains__(filter[0])):
#                self.filters[filter[1]] = stream.query.__getitem__(filter[0])

        return filters


    orders = []
    available_orders = []

    # Данные

    def get_resource(self, HttpRequest, params):
        stream = Stream(HttpRequest, params)

        input_key, field_key = self.get_keys(self.key)

        try:
            query = {
                field_key: stream.params[input_key]
            }

            stream.response = self.model.objects.get(**query)

        except self.model.DoesNotExist:
            stream.response = HttpResponseNotFound()

        return stream


    def get_collection(self, HttpRequest, params):
        stream = Stream(HttpRequest, params)

        stream.response = self.model.objects

        # Проверка и вся хуйня

        # Фильтры
        filters = self.get_filters(stream)
        stream.response = stream.response.filter(**filters)

#        print('... filters', filters)
#        print('..query..', stream.response.query)

        # Сортировка
        if (len(self.orders) > 0):
            stream.response = stream.response.order_by(*self.orders)

        # Пагинация
        stream.total = stream.response.count()
        stream.skip = stream.client_params['skip']
        stream.count = stream.client_params['count']

        if (stream.skip > stream.total):
            stream.skip = stream.total
        elif stream.skip < 0:
            stream.skip = 0

        if stream.count < 0:
            stream.count = 0
        elif stream.count > DEFAULT_PAGE_SIZE_MAX:
            stream.count = DEFAULT_PAGE_SIZE_MAX

        stream.response = stream.response[
            stream.skip : stream.skip + stream.count
        ]

        return stream

    def get_keys(self, string):
#            line = re.search(r'\s-[d]*$', string)
#            line = re.sub(r'\s-[d]*', '', string)
#            print('..', line)

        if ' as ' in string:
            orig, view = string.split(' as ')
        else:
            orig = view = string
        return orig, view

    # NOTE: Префикс используется?
    def export__resource(self, resource, schema = None, prefix = None):
        data = {};
        if type(schema) != tuple:
            schema = self.exported_data

        def get_attr_by_path(resource, path):
            key = path.pop(0)

#            print('..', key, resource)

            if ismethod(resource):
                resource = resource()

            if (resource and hasattr(resource, key)):
                value = getattr(resource, key)
            else:
                value = None
#                print(resource)
#                print(key)

            if len(path) == 0:
                if isinstance(value, datetime.time):
                    return(value.isoformat())

                if isinstance(value, datetime.datetime):
                    return(value.isoformat())

                if ismethod(value):
                    return value()

                return value
            else:
                return get_attr_by_path(value, path)

        for item in schema:
            if type(item) == str:
                orig, view = self.get_keys(item)
                if prefix:
                    orig = prefix + orig

                path = orig.split('.')
                data[view] = get_attr_by_path(resource, path)

            elif type(item) == tuple:
                orig, view = self.get_keys(item[0])
                keys = item[1]
                model = getattr(resource, orig)

                if isinstance(model, Manager):
                    resources = model.all()

                    if type(keys) == tuple:
                        data[view] = self.export(
                            resources,
                            schema = keys,
                        )
                    elif type(keys) == str:
                        data[view] = [ i[keys] for i in self.export(
                            resources,
                            schema = (keys, ),
                        )]
                    else:
                        print('*** Manager: Некорректный тип:', type(keys))

                elif isinstance(model, Model):
                    if type(keys) == str:
                        keys = (keys, )

                    if type(keys) == tuple:
                        data[view] = self.export(
                            model,
                            schema = keys,
                        )
                    else:
                        print('*** Model: Некорректный тип:', type(keys))

                else:
                    print('*** Не Менеджер! ***', manager)

            else:
                print('Что-то непонятное')

        return data

    # Конвертирование данных для выдачи
    def export(self, response, schema = None):
        if isinstance(response, QuerySet):
            if not self.exported_data:
                return None

            data = []

            # FIXME: ЗАПРОСЫ второго уровня НЕ ФИЛЬТРУЮТСЯ

#            filters = {}
#
#            for filter_key in self.__instance['filters']:
#                filter = {filter_key: self.__instance['filters'][filter_key]}
#                try:
#                    field = response.model._meta.get_field(filter_key)
#                    filters.update(filter)
#                except FieldDoesNotExist:
#                    pass
#
##            print('....', filters)
#
#            response = response.filter(**filters)

            for resource in response:
                item = self.export__resource(resource, schema)
                if item != None:
                    data.append(item)

        elif isinstance(response, Model):
            if not self.exported_data:
                return None

            data = self.export__resource(response, schema);
        else:
            return None

        return data

    def get_exported_resource(self, HttpRequest, params):
        stream = self.get_resource(HttpRequest, params)
        stream.data = self.export(stream.response)
        return stream

    def get_exported_collection(self, HttpRequest, params):
        stream = self.get_collection(HttpRequest, params)
        stream.data = self.export(stream.response)
        return stream

class ResourceMixin:
#     def __init__(self):
#         self.test = True

    '''Заголовок ресурса'''
    def head(self, HttpRequest, **kwargs):
        pass

    '''Ресурс'''
    @convert_to_json
    def get(self, HttpRequest, **kwargs):
        stream = self.get_exported_resource(HttpRequest, kwargs)
        return stream

    '''Изменение ресурса'''
    def post(self, HttpRequest, *args, **kwargs):
        pass

    '''Удаление ресурса'''
    def delete(self, HttpRequest, **kwargs):
        pass


class CollectionMixin:
    '''Заголовок коллекции'''
    def head(self, HttpRequest, **kwargs):
        pass

    '''Коллекция'''
    @convert_to_json
    def get(self, HttpRequest, **kwargs):
        stream = self.get_exported_collection(HttpRequest, kwargs)
        return stream

    '''Новый ресурс в коллекции'''
    def post(self, HttpRequest, *args, **kwargs):
        pass
