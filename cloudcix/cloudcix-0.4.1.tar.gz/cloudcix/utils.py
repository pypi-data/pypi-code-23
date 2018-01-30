# -*- coding: utf-8 -*-

"""
cloudcix.utils
~~~~~~~~~~~~~~

This module implements the CloudCIX API JSON Encodes and Decoders
"""

import datetime
from dateutil import parser
import decimal
import json
import uuid
import warnings

from cloudcix.auth import AdminSession


class JSONEncoder(json.JSONEncoder):
    """
    JSONEncoder that can encode date/time/timedelta, decimal and other python
    objects into JSON. Inspired by Django Rest Framework
    """

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            rep = obj.isoformat()
            if rep.endswith('+00:00'):
                rep = rep[:-6] + 'Z'
            return rep
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, datetime.time):
            # Check to ensure the time isn't timezone aware
            if obj.utcoffset() is not None:
                raise ValueError(
                    "JSON cannot represent timezone-aware times"
                )
            rep = obj.isoformat()
            if obj.microsecond:
                rep = rep[:12]
            return rep
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, uuid.UUID):
            return str(obj)
        elif hasattr(obj, '__getitem__'):
            try:
                return dict(obj)
            except (KeyError, ValueError):
                pass
        elif hasattr(obj, '__iter__'):
            return tuple(item for item in obj)
        return super(JSONEncoder, self).default(obj)


class JSONDecoder(json.JSONDecoder):
    """
    JSONDecoder that can decode date/time/timedelta, decimal and other strings
    into python objects
    """

    def __init__(self, *args, **kwargs):
        kwargs.pop('encoding')
        super(JSONDecoder, self).__init__(
            *args,
            object_hook=self.parse,
            parse_float=decimal.Decimal,
            **kwargs
        )

    def parse(self, obj):
        if hasattr(obj, 'items'):
            for k, v in obj.items():
                obj[k] = self.parse(v)
        elif isinstance(obj, str):
            try:
                return datetime.datetime.strptime(obj, '%H:%M:%S.%f').time()
            except ValueError:
                pass  # Not a timestamp
            try:
                return datetime.datetime.strptime(obj, '%Y-%m-%d').date()
            except ValueError:
                pass  # Not a date
            try:
                return parser.parse(obj)
            except ValueError:
                pass  # Not a parsable datetime string
        return obj


def get_admin_session():
    """
    Backwards compatibility function with older version of python-cloudcix
    DEPRECATED and will be removed sometime
    :return: An instance of cloudcix.auth.AdminSession
    """
    warnings.warn(
        ('utils.get_admin_session is a function for backwards compatibility'
         'and is deprecated. It will be removed in v1 so please'
         'replace the function call with AdminSession() directly'),
        DeprecationWarning
    )
    return AdminSession()
