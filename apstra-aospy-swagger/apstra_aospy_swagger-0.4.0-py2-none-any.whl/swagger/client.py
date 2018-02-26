# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula

import os

import halutz.client
from halutz.utils import assign_operation_ids

from bravado_core.formatter import SwaggerFormat, NO_OP
from aospy.client import Client as AOSpy

__all__ = ['Client']


class Client(halutz.client.Client):

    def __init__(self, server_url=None, **options):

        if not server_url:
            try:
                server_url = 'https://%s' % os.environ['AOS_SERVER']
            except KeyError:
                raise RuntimeError('missing AOS_SERVER in env')

        if not options.get('remote'):
            options['remote'] = AOSpy(server_url)
            options['session'] = options['remote'].api

        super(Client, self).__init__(server_url, **options)

    @classmethod
    def from_aospy(cls, aospy_client):
        return cls(server_url=aospy_client.url,
                   session=aospy_client.api,
                   remote=aospy_client)

    def fetch_swagger_spec(self):
        aospy = self.remote
        origin_spec = aospy.fetch_apispec()

        api_ver = aospy.version_info['api_version_parsed']
        parsed_version = type(api_ver)

        if api_ver >= parsed_version('2.1'):
            from .operationids import OPERATION_IDS_AOS_2_1
            assign_operation_ids(origin_spec, OPERATION_IDS_AOS_2_1)

        return origin_spec

    def make_swagger_spec(self):
        swag = super(Client, self).make_swagger_spec()

        # AOS spec defines a string format.  TODO: need to investigate
        swag.register_format(SwaggerFormat(
            'string', str, str, NO_OP,
            'handles string format'))

        return swag
