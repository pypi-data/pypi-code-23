# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#

import logging

from .runtime_infos import RuntimeInfos

LOGGER = logging.getLogger(__name__)


class PayloadCreator(object):
    """Create attack payloads."""

    SECTIONS = (
        'request',
        'params',
        'headers',
        'local',
    )

    @classmethod
    def get_payload(cls, request, sections=None):
        if sections is None:
            sections = cls.SECTIONS
        payload = {}
        if 'request' in sections:
            payload['request'] = request.request_payload
        if 'params' in sections:
            # Don't send cookies and messages.
            payload['params'] = {
                'form': request.form_params,
                'query': request.query_params,
                'other': request.view_params,
                'json': request.json_params,
            }
        if 'headers' in sections:
            payload['headers'] = request.get_client_ips_headers()
        if 'local' in sections:
            payload['local'] = RuntimeInfos.local_infos()
        return payload
