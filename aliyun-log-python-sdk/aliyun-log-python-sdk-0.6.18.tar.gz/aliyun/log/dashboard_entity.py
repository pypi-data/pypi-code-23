#!/usr/bin/env python
# encoding: utf-8

# Copyright (C) Alibaba Cloud Computing
# All rights reserved.


from .logresponse import LogResponse
from .logexception import LogException
import logging

logger = logging.getLogger(__name__)


class GetDashboardResponse(LogResponse):
    """ The response of the get_dashboard API

    :type header: dict
    :param header: GetLogtailConfigResponse HTTP response header

    :type resp: dict
    :param resp: the HTTP response body
    """

    def __init__(self, resp, header):
        LogResponse.__init__(self, header, resp)
        