# coding: utf-8

from __future__ import absolute_import

import json
import enum
import datetime


class ComplexJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "__json__"):
            return obj.__json__()
        else:
            if isinstance(obj, enum.Enum):
                return obj.value
            elif isinstance(obj, datetime.datetime):
                return obj.isoformat()[0:-3]
            elif isinstance(obj, datetime.date):
                return obj.isoformat()
            else:
                return json.JSONEncoder.default(self, obj)