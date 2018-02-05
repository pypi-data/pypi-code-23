# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula

OPERATION_IDS_AOS_2_1 = {

    # system

    "/api/hcl": {
        'get':      'get_hcls',
        'post':     'create_hcl'
    },

    "/api/design/logical-devices": {
        'get':      'get_logical_devices',
        'post':     'create_logical_device'
    },

    "/api/design/logical-device-maps": {
        'get':      'get_logical_device_maps',
        'post':     'create_logical_device_map'
    },

    "/api/design/rack-types": {
        'get':      'get_rack_types',
        'post':     'create_rack_type'

    },

    "/api/blueprints/{blueprint_id}/probes": {
        'get':      'get_all_iba_probes',
        'post':     'create_iba_probe'
    },

    "/api/blueprints/{blueprint_id}/probes/{probe_id}": {
        'get':      'get_iba_probe',
        'delete':   'delete_iba_probe'
    },

    # facade

    "/api/blueprints/{blueprint_id}/cabling-map": {
        "get":      "get_cabling_map"
    },

    "/api/blueprints/{blueprint_id}/virtual-networks": {
        'get':      'get_virtual_networks',
        'post':     'create_virtual_network'
    },

    "/api/blueprints/{blueprint_id}/virtual-networks/{virtual_network_id}": {
        'get':      'get_virtual_network',
        'delete':   'delele_virtual_network',
        'patch':    'update_virtual_network'
    },

    "/api/blueprints/{blueprint_id}/racks": {
        'get':      'get_racks'
    },

    "/api/blueprints/{blueprint_id}/resource_groups": {
        'get':      'get_resource_groups'
    },

    "/api/blueprints/{blueprint_id}/resource_groups/{resource_type}/{group_name}": {
        'put':      'set_resource_group'
    }

}
