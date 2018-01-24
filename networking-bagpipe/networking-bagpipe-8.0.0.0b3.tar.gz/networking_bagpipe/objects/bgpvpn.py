#   Copyright (c) 2017 Orange.  # All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_log import log as logging
from oslo_versionedobjects import fields as obj_fields

from networking_bgpvpn.neutron.db import bgpvpn_db

from neutron.api.rpc.callbacks import resources
from neutron.common import utils
from neutron.db import api as db_api
from neutron.objects import base
from neutron.objects import common_types
from neutron.objects.ports import IPAllocation
from neutron.objects.ports import Port
from neutron.objects.router import RouterPort
from neutron.objects.subnet import Subnet

from neutron_lib.api.definitions import bgpvpn as bgpvpn_api
from neutron_lib.api.definitions import bgpvpn_routes_control as bgpvpn_rc_api
from neutron_lib import constants

LOG = logging.getLogger(__name__)


def _get_gateway_mac_by_subnet(obj_context, subnet):
    if not subnet.gateway_ip:
        LOG.error("no gateway IP defined for subnet %s", subnet)
        return None

    ip_allocation = IPAllocation.get_object(obj_context,
                                            network_id=subnet.network_id,
                                            subnet_id=subnet.id,
                                            ip_address=subnet.gateway_ip)
    if ip_allocation:
        port = Port.get_object(obj_context, id=ip_allocation.port_id)
        return str(port.mac_address)
    else:
        LOG.debug("no port allocated to gateway IP for subnet %s", subnet.id)
        return None


def _get_subnets_info(obj_context, net_id):
    subnets = Subnet.get_objects(obj_context, network_id=net_id)
    return [
        {'ip_version': subnet.ip_version,
         'cidr': subnet.cidr,
         'gateway_ip': subnet.gateway_ip,
         'gateway_mac': _get_gateway_mac_by_subnet(obj_context, subnet)
         }
        for subnet in subnets
    ]


class BGPVPNTypeField(obj_fields.AutoTypedField):
    AUTO_TYPE = obj_fields.Enum(valid_values=bgpvpn_api.BGPVPN_TYPES)


@base.NeutronObjectRegistry.register
class BGPVPN(base.NeutronDbObject):
    # Version 1.0: Initial version
    VERSION = '1.0'

    db_model = bgpvpn_db.BGPVPN
    fields = {
        'id': common_types.UUIDField(),
        'project_id': obj_fields.StringField(),
        'type': BGPVPNTypeField(),
        'name': obj_fields.StringField(),
        'route_targets': obj_fields.ListOfStringsField(nullable=True),
        'import_targets': obj_fields.ListOfStringsField(nullable=True),
        'export_targets': obj_fields.ListOfStringsField(nullable=True),
        'route_distinguishers': obj_fields.ListOfStringsField(nullable=True),
        'local_pref': obj_fields.IntegerField(nullable=True),
    }

    foreign_keys = {'BGPVPNNetAssociation': {'id': 'bgpvpn_id'},
                    'BGPVPNRouterAssociation': {'id': 'bgpvpn_id'},
                    'BGPVPNPortAssociation': {'id': 'bgpvpn_id'}}

    @classmethod
    def modify_fields_from_db(cls, db_obj):
        result = super(BGPVPN, cls).modify_fields_from_db(db_obj)
        for field in ['route_targets',
                      'import_targets',
                      'export_targets',
                      'route_distinguishers']:
            if field in result:
                result[field] = (result[field].split(',')
                                 if result[field] else [])
        return result

    @classmethod
    def modify_fields_to_db(cls, fields):
        result = super(BGPVPN, cls).modify_fields_to_db(fields)
        for field in ['route_targets',
                      'import_targets',
                      'export_targets',
                      'route_distinguishers']:
            if field in result:
                result[field] = ','.join(result.get(field, []))
        return result


@base.NeutronObjectRegistry.register
class BGPVPNNetAssociation(base.NeutronDbObject):
    # Version 1.0: Initial version
    VERSION = '1.0'

    db_model = bgpvpn_db.BGPVPNNetAssociation

    fields = {
        'id': common_types.UUIDField(),
        'project_id': obj_fields.StringField(),
        'bgpvpn_id': obj_fields.StringField(),
        'bgpvpn': obj_fields.ObjectField('BGPVPN'),
        'network_id': obj_fields.StringField(),
        'subnets': common_types.ListOfDictOfMiscValuesField(nullable=True)
    }

    synthetic_fields = ['bgpvpn',
                        'subnets']

    def __init__(self, context=None, **kwargs):
        super(BGPVPNNetAssociation, self).__init__(context, **kwargs)

    def create(self):
        with db_api.autonested_transaction(self.obj_context.session):
            super(BGPVPNNetAssociation, self).create()
            self.obj_load_attr('subnets')

    def obj_load_attr(self, attrname):
        if attrname == 'subnets':
            self._load_subnets()
        else:
            super(BGPVPNNetAssociation, self).obj_load_attr(attrname)

    def _load_subnets(self, db_obj=None):
        # pylint: disable=no-member
        subnets_info = _get_subnets_info(self.obj_context, self.network_id)
        setattr(self, 'subnets', subnets_info)
        self.obj_reset_changes(['subnets'])

    def from_db_object(self, obj):
        super(BGPVPNNetAssociation, self).from_db_object(obj)
        self._load_subnets(obj)

    def all_subnets(self, network_id):
        # pylint: disable=no-member
        return self.subnets


@base.NeutronObjectRegistry.register
class BGPVPNRouterAssociation(base.NeutronDbObject):
    # Version 1.0: Initial version
    VERSION = '1.0'

    db_model = bgpvpn_db.BGPVPNRouterAssociation

    fields = {
        'id': common_types.UUIDField(),
        'project_id': obj_fields.StringField(),
        'bgpvpn_id': obj_fields.StringField(),
        'bgpvpn': obj_fields.ObjectField('BGPVPN'),
        'router_id': obj_fields.StringField(),
        'connected_networks':
            common_types.ListOfDictOfMiscValuesField(nullable=True)
    }

    synthetic_fields = ['bgpvpn',
                        'connected_networks']

    def __init__(self, context=None, **kwargs):
        super(BGPVPNRouterAssociation, self).__init__(context, **kwargs)

    def create(self):
        with db_api.autonested_transaction(self.obj_context.session):
            super(BGPVPNRouterAssociation, self).create()
            self.obj_load_attr('connected_networks')

    def update(self):
        with db_api.autonested_transaction(self.obj_context.session):
            if 'connected_networks' in self.obj_what_changed():
                self.obj_load_attr('connected_networks')
            super(BGPVPNRouterAssociation, self).update()

    def obj_load_attr(self, attrname):
        if attrname == 'connected_networks':
            return self._load_connected_networks()
        super(BGPVPNRouterAssociation, self).obj_load_attr(attrname)

    @classmethod
    def get_objects(cls, context, _pager=None, validate_filters=True,
                    **kwargs):
        if 'network_id' in kwargs:
            # TODO(tmorin): this is very inefficient, on a deployment with a
            # large number of Router Associations, this method will look at all
            # of them, even if our network is not connected to any Router.
            # I believe that starting from the network, finding which are the
            # routers connected to it, and then finding if there are
            # RouterAssociations for these routers, would be much more
            # efficient.
            network_id = kwargs.pop('network_id')
            router_assocs = super(BGPVPNRouterAssociation, cls).get_objects(
                context, _pager=_pager, validate_filters=validate_filters,
                **kwargs)
            router_assocs = cls._filter_router_assoc_by_network(router_assocs,
                                                                network_id)
            return router_assocs

        return super(BGPVPNRouterAssociation, cls).get_objects(
            context, _pager=_pager, validate_filters=validate_filters,
            **kwargs)

    def _load_connected_networks(self, db_obj=None):
        # NOTE(tmorin): can be improved by directly looking up
        # Ports with device_id=self.router_id
        router_ports = RouterPort.get_objects(
            self.obj_context,
            router_id=self.router_id)  # pylint: disable=no-member
        connected_networks = []
        for router_port in router_ports:
            port = Port.get_object(self.obj_context,
                                   id=router_port.port_id)
            if port:
                # router gateway networks are not considered as requiring
                # to be bound to BGPVPNs
                if port.device_owner == constants.DEVICE_OWNER_ROUTER_GW:
                    LOG.debug("skipping port %s, because router gateway",
                              port.id)
                    continue
                connected_networks.append({
                    'network_id': port.network_id,
                    'subnets': _get_subnets_info(self.obj_context,
                                                 port.network_id)
                })
            else:
                LOG.warning("Couldn't find Port for RouterPort (router:%s,"
                            "port:%s)", router_port.router_id,
                            router_port.port_id)
        setattr(self, 'connected_networks', connected_networks)
        self.obj_reset_changes(['connected_networks'])

    def from_db_object(self, obj):
        super(BGPVPNRouterAssociation, self).from_db_object(obj)
        self._load_connected_networks(obj)

    @classmethod
    def _filter_router_assoc_by_network(self, router_associations, net_id):
        router_associations_filtered = []
        for router_association in router_associations:
            for connected_network in router_association.connected_networks:
                if connected_network['network_id'] == net_id:
                    router_associations_filtered.append(router_association)
                    break
        return router_associations_filtered

    def all_subnets(self, network_id):
        # pylint: disable=no-member
        for connected_net in self.connected_networks:
            if connected_net['network_id'] == network_id:
                return connected_net['subnets']
        return []


@base.NeutronObjectRegistry.register
class BGPVPNPortAssociation(base.NeutronDbObject):
    # Version 1.0: Initial version
    VERSION = '1.0'

    db_model = bgpvpn_db.BGPVPNPortAssociation

    fields = {
        'id': common_types.UUIDField(),
        'project_id': obj_fields.StringField(),
        'bgpvpn_id': obj_fields.StringField(),
        'bgpvpn': obj_fields.ObjectField('BGPVPN'),
        'port_id': obj_fields.StringField(),
        'subnets': common_types.ListOfDictOfMiscValuesField(nullable=True),
        'routes': obj_fields.ListOfObjectsField('BGPVPNPortAssociationRoute'),
        'advertise_fixed_ips': obj_fields.BooleanField(default=True)
    }

    synthetic_fields = ['bgpvpn',
                        'subnets',
                        'routes']

    def __init__(self, context=None, **kwargs):
        super(BGPVPNPortAssociation, self).__init__(context, **kwargs)

    def create(self):
        with db_api.autonested_transaction(self.obj_context.session):
            super(BGPVPNPortAssociation, self).create()
            self.obj_load_attr('subnets')

    def obj_load_attr(self, attrname):
        if attrname == 'subnets':
            self._load_subnets()
        else:
            super(BGPVPNPortAssociation, self).obj_load_attr(attrname)

    def _load_subnets(self, db_obj=None):
        # pylint: disable=no-member
        port = Port.get_object(self.obj_context, id=self.port_id)
        subnets_info = _get_subnets_info(self.obj_context, port.network_id)
        setattr(self, 'subnets', subnets_info)
        self.obj_reset_changes(['subnets'])

    def from_db_object(self, obj):
        super(BGPVPNPortAssociation, self).from_db_object(obj)
        self._load_subnets(obj)

    def all_subnets(self, network_id):
        # pylint: disable=no-member
        return self.subnets


class BGPVPNPortAssociationRouteTypeField(obj_fields.AutoTypedField):
    AUTO_TYPE = obj_fields.Enum(valid_values=bgpvpn_rc_api.ROUTE_TYPES)


@base.NeutronObjectRegistry.register
class BGPVPNPortAssociationRoute(base.NeutronDbObject):
    # Version 1.0: Initial version
    VERSION = '1.0'

    db_model = bgpvpn_db.BGPVPNPortAssociationRoute

    fields = {
        'id': common_types.UUIDField(),
        'port_association_id': common_types.UUIDField(),
        'type': BGPVPNPortAssociationRouteTypeField(),
        'prefix': common_types.IPNetworkField(),
        'local_pref': obj_fields.IntegerField(nullable=True)
    }

    foreign_keys = {'BGPVPNPortAssociation': {'port_association_id': 'id'}
                    }

    @classmethod
    def modify_fields_from_db(cls, db_obj):
        fields = super(BGPVPNPortAssociationRoute,
                       cls).modify_fields_from_db(db_obj)
        if 'prefix' in fields and fields['prefix'] is not None:
            fields['prefix'] = utils.AuthenticIPNetwork(fields['prefix'])
        return fields

    @classmethod
    def modify_fields_to_db(cls, fields):
        result = super(BGPVPNPortAssociationRoute,
                       cls).modify_fields_to_db(fields)
        if 'prefix' in result and result['prefix'] is not None:
            result['prefix'] = cls.filter_to_str(result['prefix'])
        return result


resources.register_resource_class(BGPVPN)
resources.register_resource_class(BGPVPNNetAssociation)
resources.register_resource_class(BGPVPNRouterAssociation)
resources.register_resource_class(BGPVPNPortAssociation)
