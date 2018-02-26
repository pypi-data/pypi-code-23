# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula

"""
This file contains code used to patch the AOS swagger spec due to known issues
in various releases
"""

import six
from inflection import underscore


def bugfix_PostApiBlueprintsBlueprintIdProbesRequest(spec):
    # AOS-6405
    schema = spec['definitions']['PostApiBlueprintsBlueprintIdProbesRequest']
    props = schema['properties']['processors']['items']['properties']['properties']
    del props['maxProperties']
    del props['additionalProperties']


def bugfix_facade_resource_groups(origin_spec):

    spec_paths = origin_spec['paths']

    # need to remove the schema definition for this path due to bug.

    path = spec_paths["/api/blueprints/{blueprint_id}/resource_groups"]
    resp_200 = path['get']['responses']['200']
    if 'schema' in resp_200:
        del resp_200['schema']

    # the PUT for this path returns a 202, even though the spec shows 204

    path = spec_paths["/api/blueprints/{blueprint_id}/resource_groups/{resource_type}/{group_name}"]
    resps = path['put']['responses']
    resps['202'] = resps['204']


def patch_aos_2_1_platform(spec):

    # convert the use of hyphens to underscores

    for path_name, path_data in six.iteritems(spec['paths']):
        for method, method_data in six.iteritems(path_data):
            method_data['tags'] = map(underscore, method_data['tags'])

    for model in [
        # 'GetApiBlueprintsBlueprintIdPropertySetsResponse', -- removed, used but not defined.
        # 'GetApiBlueprintsBlueprintIdResourceGroupsResponse' -- ""
        # 'PatchApiBlueprintsBlueprintIdNodesRequest',
            'GetApiDesignRackTypesResponse']:
        array_to_object(spec['definitions'][model])

    # spot-fixes
    bugfix_PostApiBlueprintsBlueprintIdProbesRequest(spec)


def patch_aos_2_1_reference_design(spec):

    for path_name, path_data in six.iteritems(spec['paths']):
        for method, method_data in six.iteritems(path_data):

            method_data['tags'].pop()       # remove the mangled tag value
            method_data['tags'].insert(0, 'blueprints')

            # need to patch the response status_code values, because the
            # AOS spec for the facade API hardcodes these to 200.

            resp = method_data['responses']
            if method == 'post' and ('201' not in resp):
                resp['201'] = resp.pop('200')
            elif method in ['put', 'patch', 'delete'] and ('204' not in resp):
                resp['204'] = resp.pop('200')

    # there are a few definitions that have invalid schema default values. we need to
    # sanatize these now before they are used by the client body class builder
    # otherwise that code will raise exceptions (python-jsonschema-objects).

    for model in ['PostApiBlueprintsBlueprintIdVirtualNetworksRequest',
                  'PostApiBlueprintsBlueprintIdVirtualNetworksVirtualNetworkIdEndpointsRequest',
                  'PutApiBlueprintsBlueprintIdVirtualNetworksVirtualNetworkIdRequest']:
        sanitize_defaults(spec['definitions'][model])

    # spot-fixes
    bugfix_facade_resource_groups(spec)


def sanitize_defaults(spec):
    """
    This function traverses the schema spec and finds any 'default' values that are
    not explicity None but have none-ish values; for example a string default of ''.

    This fucntion uses the 'stack of iterators' design pattern, see
    http://garethrees.org/2016/09/28/pattern
    """

    stack = [six.iteritems(spec['properties'])]
    while stack:
        for prop_name, prop_val in stack[-1]:
            default = prop_val.get('default')

            if (default is not None) and (not default):
                prop_val['default'] = None

            if 'items' in prop_val and prop_val['type'] == 'array':
                stack.append(six.iteritems(prop_val['items']['properties']))
                break
        else:
            stack.pop()


def array_to_object(schema):
    items = schema.pop('items')
    schema['type'] = 'object'
    schema['required'] = ['items']
    schema['properties'] = {
        'items': {
            'items': items,
            'type': 'array'
        }
    }
