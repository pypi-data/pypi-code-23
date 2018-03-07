#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from rest_framework.response import Response


class SimpleResponse(Response):
    """
    封装http相应
    """

    def __init__(self, data, status=200, *args, **kwargs):
        if not isinstance(data, (dict, list)):
            raise Exception("data format error")
        super(SimpleResponse, self).__init__(data, status=status, *args, **kwargs)
