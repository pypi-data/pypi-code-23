# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula

import halutz.client
from halutz.utils import assign_operation_ids

__all__ = ['Client']


def patch_bugs(origin_spec):
    path = origin_spec['paths']["/api/blueprints/{blueprint_id}/resource_groups"]
    resp_200 = path['get']['responses']['200']
    if 'schema' in resp_200:
        del resp_200['schema']


class Client(halutz.client.Client):

    def __init__(self, aos_client=None, **halutz_kwargs):
        kwargs = halutz_kwargs or {}

        if not aos_client:
            from aospy.client import Client as AOSpy
            aos_client = AOSpy(kwargs.get('server_url'))

        kwargs['server_url'] = aos_client.url
        kwargs['session'] = aos_client.api
        kwargs['remote'] = aos_client

        super(Client, self).__init__(**kwargs)

    def fetch_swagger_spec(self):
        aospy = self.remote
        origin_spec = aospy.fetch_apispec()

        aos_ver = aospy.version_info['parsed']
        parsed_version = type(aos_ver)

        if parsed_version('2.1') <= aos_ver <= parsed_version('2.2'):
            from .operationids import OPERATION_IDS_AOS_2_1
            assign_operation_ids(origin_spec, OPERATION_IDS_AOS_2_1)
            patch_bugs(origin_spec)

        return origin_spec
