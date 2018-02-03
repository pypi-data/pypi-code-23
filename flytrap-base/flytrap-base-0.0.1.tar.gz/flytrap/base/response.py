#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
import json
from django.http import HttpResponse


class SimpleResponse(HttpResponse):
    """
    封装http相应
    """

    def __init__(self, data, status=200, *args, **kwargs):
        if not isinstance(data, dict):
            raise Exception("data format error")
        super(SimpleResponse, self).__init__(json.dumps(data), status=status, *args, **kwargs)
