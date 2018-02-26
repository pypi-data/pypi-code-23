# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula

API_RESOURCES = "/api/resources"
API_BLUEPRINT = "/api/blueprints/{blueprint_id}"
API_VNET = API_BLUEPRINT + "/virtual-networks/{virtual_network_id}"

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

    # Resources

    API_RESOURCES + "/ip-pools": {
        'get':      'get_ip_pools',
        'post':     'create_ip_pool'
    },

    API_RESOURCES + "/asn-pools": {
        'get':      'get_asn_pools',
        'post':     'create_asn_pool'
    },

    API_RESOURCES + "/external-routers": {
        'get': 'get_external_routers'
    },

    # Blueprints

    API_BLUEPRINT + "/probes": {
        'get':      'get_probes',
        'post':     'create_probe'
    },

    API_BLUEPRINT + "/probes/{probe_id}": {
        'get':      'get_probe',
        'delete':   'delete_probe'
    },

    API_BLUEPRINT + "/cabling-map": {
        "get":      "get_cabling_map"
    },

    API_BLUEPRINT + "/racks": {
        'get':      'get_racks'
    },

    API_BLUEPRINT + "/resource_groups": {
        'get':      'get_resource_groups'
    },

    API_BLUEPRINT + "/resource_groups/{resource_type}/{group_name}": {
        'put':      'set_resource_group'
    },

    API_BLUEPRINT + "/logical-device-map-assignments": {
        'put':      'set_logical_device_maps'
    },

    # virtual-network related

    API_BLUEPRINT + "/virtual-networks": {
        'get':      'get_virtual_networks',
        'post':     'create_virtual_network'
    },

    API_BLUEPRINT + "/external-router-assignments": {
        'patch':    'update_external_routers'
    },

    API_VNET: {
        'get':      'get_virtual_network',
        'delete':   'delete_virtual_network',
        'patch':    'update_virtual_network'
    },

    API_VNET + "/endpoints": {
        'post':     'create_virtual_network_endpoint'
    },

    API_VNET + "/endpoints/{endpoint_id}": {
        'delete':   'delete_virtual_network_endpoint'
    },
}
