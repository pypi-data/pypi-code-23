import datetime

import six
from django.core.paginator import Page
from django.db import models
from django.utils.encoding import force_text
from django.conf import settings
from django import forms


class BaseSerializer(object):
    formats = ['json']

    def __init__(self, datetime_formatting=None, fields=None):
        self._fields = fields

        if datetime_formatting is not None:
            self.datetime_formatting = datetime_formatting
        else:
            self.datetime_formatting = getattr(settings, 'RESTIFY_DATETIME_FORMATTING', '%Y-%m-%d %H:%M:%S%z')

    def flatten(self, data, fields=None):
        """
        For a piece of data, attempts to recognize it and provide a simplified
        form of something complex.

        This brings complex Python data structures down to native types of the
        serialization format(s).
        """
        if fields is None and self._fields is not None:
            fields = self._fields

        if isinstance(data, (list, tuple)):
            return [self.flatten(item, fields=fields) for item in data]
        elif isinstance(data, dict):
            return dict((key, self.flatten(val, fields=fields)) for (key, val) in data.items())
        elif isinstance(data, (datetime.datetime, datetime.date)):
            return data.strftime(self.datetime_formatting)
        elif isinstance(data, (int, float)):
            return data
        elif data is None:
            return data
        elif fields:
            retval = dict()
            for field in fields:
                if isinstance(field, six.string_types):
                    val = getattr(data, field)
                    retval[field] = self.flatten(val, fields=[])
                elif isinstance(field, (tuple, list)):
                    val = getattr(data, field[0])
                    retval[field[0]] = self.flatten(val, fields=field[1])
            return retval
        elif hasattr(data, 'flatten'):
            return data.flatten()

        return force_text(data)


class DjangoSerializer(BaseSerializer):
    def flatten(self, data, fields=None):
        if isinstance(data, Page):
            retval = {
                'current': data.number,
                'num_pages': data.paginator.num_pages,
                'list': []
            }

            # Previous page
            previous = None
            if data.has_previous():
                number = data.previous_page_number()
                previous = {
                    'key': number,
                    'value': number
                }
            retval['list'].append(previous)

            # Current page must be at index #1 (because reply['pages']['current'] is initialized to 1)
            retval['list'].append({
                'key': data.number,
                'value': data.number
            })

            # Next page
            next = None
            if data.has_next():
                number = data.next_page_number()
                next = {
                    'key': number,
                    'value': number
                }
            retval['list'].append(next)

            return retval

        return super().flatten(data, fields=fields)


class ModelSerializer(DjangoSerializer):
    def flatten(self, data, fields=None):
        if fields is None and self._fields is not None:
            fields = self._fields

        if isinstance(data, (forms.ModelForm, forms.Form,)):
            retval = {}
            if data.is_valid() or not data.is_bound:
                for field in data:
                    if hasattr(field.field, 'queryset'): ### ForeignKey, ManyToManyField
                        retval[field.name] = field.value() or ''
                    else:
                        retval[field.name] = field.value()
            else:
                retval = {key: list(value) for key, value in data.errors.items()}
            return retval

        elif isinstance(data, models.Model):
            if fields is None:
                fields = [field.name for field in data._meta.fields]

            if data._meta.pk.name not in fields:
                fields = tuple(fields) + (data._meta.pk.name,)

            return super().flatten(data, fields)

        elif hasattr(data, 'through') and hasattr(data, 'all'): #m2m relation
            return super().flatten(list(data.all()), fields)

        elif isinstance(data, models.QuerySet):
            return super().flatten(list(data), fields)

        return super().flatten(data, fields=fields)
