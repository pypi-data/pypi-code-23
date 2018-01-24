# vim: tabstop=4 shiftwidth=4 softtabstop=4
# encoding: utf-8

# Copyright 2014 Orange
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import abc
import collections
import copy
import re
import socket
import threading

import netaddr
from oslo_log import log as logging
import six

from networking_bagpipe.bagpipe_bgp.common import exceptions as exc
from networking_bagpipe.bagpipe_bgp.common import log_decorator
from networking_bagpipe.bagpipe_bgp.common import looking_glass as lg
from networking_bagpipe.bagpipe_bgp.common import utils
from networking_bagpipe.bagpipe_bgp import engine
from networking_bagpipe.bagpipe_bgp.engine import exa
from networking_bagpipe.bagpipe_bgp.engine import flowspec
from networking_bagpipe.bagpipe_bgp.engine import tracker_worker

LOG = logging.getLogger(__name__)

DEFAULT_LOCAL_PREF = 100


class TrafficClassifier(object):

    def __init__(self, source_prefix=None, destination_prefix=None,
                 source_port=None, destination_port=None, protocol='tcp'):
        self.source_pfx = source_prefix
        self.destination_pfx = destination_prefix

        if source_port:
            if ":" in source_port:
                self.source_port = tuple(
                    [int(p) for p in source_port.split(":")]
                )
            else:
                self.source_port = int(source_port)
        else:
            self.source_port = source_port

        if destination_port:
            if ":" in destination_port:
                self.destination_port = tuple(
                    [int(p) for p in destination_port.split(":")]
                )
            else:
                self.destination_port = int(destination_port)
        else:
            self.destination_port = destination_port

        self.protocol = protocol

    def __repr__(self):
        return "traffic-classifier:%s" % str(self)

    def __str__(self):
        return "%s-%s,%s-%s,%s" % (self.source_pfx or "*",
                                   self.source_port or "*",
                                   self.destination_pfx or "*",
                                   self.destination_port or "*",
                                   self.protocol)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                self.__dict__ == other.__dict__)

    def __hash__(self):
        return hash((self.source_pfx, self.source_port,
                     self.destination_pfx, self.destination_port,
                     self.protocol))

    def _interpret_port_rule(self, rule):
        if len(rule) == 1:
            op = rule[0].operations
            port = rule[0].value
            if op == '>=':
                port_range = (int(port), 65535)
            elif op == '<=':
                port_range = (0, int(port))
            elif op == '>':
                port_range = (int(port)+1, 65535)
            elif op == '<':
                port_range = (0, int(port)-1)
            else:
                port_range = int(port)
        else:
            port_range = ()
            for elem in rule:
                op = elem.operations
                port = elem.value
                if op == '>=' or op == '<=':
                    port_range += int(port)
                elif op == '>':
                    port_range += int(port)+1
                elif op == '<':
                    port_range += int(port)-1

        return port_range

    @log_decorator.log
    def _construct_port_rules(self, port_range, flow_object):
        LOG.info("Construct port rules with %s (type %s) on %s object",
                 port_range, type(port_range), flow_object)
        port_rules = list()

        # Check if port range or port number
        if type(port_range) == tuple:
            port_min, port_max = port_range

            if int(port_min) == 0:
                # Operator <
                port_rules.append(flow_object(exa.flow.NumericOperator.LT,
                                              port_max))
            elif int(port_max) == 65535:
                # Operator >
                port_rules.append(flow_object(exa.flow.NumericOperator.GT,
                                              port_min))
            else:
                # Operator >=
                gt_eq_op = (exa.flow.NumericOperator.GT |
                            exa.flow.NumericOperator.EQ)
                # Operator &<=
                lt_eq_op = (exa.flow.NumericOperator.AND |
                            exa.flow.NumericOperator.LT |
                            exa.flow.NumericOperator.EQ)
                port_rules.append(flow_object(gt_eq_op, port_min))
                port_rules.append(flow_object(lt_eq_op, port_max))
        else:
            port_rules.append(flow_object(exa.flow.NumericOperator.EQ,
                                          port_range))

        return port_rules

    def _get_source_prefix(self, rule):
        self.source_pfx = rule[0].cidr.prefix()

    def _get_destination_prefix(self, rule):
        self.destination_pfx = rule[0].cidr.prefix()

    def _parse_any_port(self, rule):
        self.source_port = self._interpret_port_rule(rule)
        self.destination_port = list(self.source_port)

    def _parse_source_port(self, rule):
        self.source_port = self._interpret_port_rule(rule)

    def _parse_destination_port(self, rule):
        self.destination_port = self._interpret_port_rule(rule)

    def _get_protocol(self, rule):
        self.protocol = exa.Protocol.names[rule[0].value]

    def map_traffic_classifier_2_redirect_rules(self):
        rules = list()
        if self.source_pfx:
            ip, mask = self.source_pfx.split('/')
            if netaddr.IPNetwork(self.source_pfx).version == 4:
                rules.append(
                    exa.flow.Flow4Source(socket.inet_pton(socket.AF_INET, ip),
                                         int(mask)))
            elif netaddr.IPNetwork(self.source_pfx).version == 6:
                # TODO(xxx): IPv6 offset ??
                rules.append(
                    exa.flow.Flow6Source(socket.inet_pton(socket.AF_INET6, ip),
                                         int(mask), 0))

        if self.destination_pfx:
            ip, mask = self.destination_pfx.split('/')
            if netaddr.IPNetwork(self.destination_pfx).version == 4:
                rules.append(
                    exa.flow.Flow4Destination(socket.inet_pton(socket.AF_INET,
                                                               ip),
                                              int(mask))
                )
            elif netaddr.IPNetwork(self.destination_pfx).version == 6:
                # TODO(xxx): IPv6 offset ??
                rules.append(
                    exa.flow.Flow6Destination(socket.inet_pton(socket.AF_INET6,
                                                               ip),
                                              int(mask), 0)
                )

        if self.source_port:
            rules += self._construct_port_rules(self.source_port,
                                                exa.flow.FlowSourcePort)

        if self.destination_port:
            rules += self._construct_port_rules(self.destination_port,
                                                exa.flow.FlowDestinationPort)

        if self.protocol:
            rules.append(exa.flow.FlowIPProtocol(exa.flow.NumericOperator.EQ,
                                                 exa.Protocol.named(
                                                     self.protocol)
                                                 ))

        return rules

    def map_redirect_rules_2_traffic_classifier(self, rules):
        components = {1: self._get_destination_prefix,  # FlowDestinationPrefix
                      2: self._get_source_prefix,  # FlowSourcePrefix
                      3: self._get_protocol,  # FlowIPProtocol
                      4: self._parse_any_port,  # FlowAnyPort
                      5: self._parse_destination_port,  # FLowDestinationPort
                      6: self._parse_source_port}  # FlowSourcePort

        for ID, rule in six.iteritems(rules):
            components[ID](rule)


@six.add_metaclass(abc.ABCMeta)
class VPNInstance(tracker_worker.TrackerWorker,
                  threading.Thread,
                  lg.LookingGlassLocalLogger):

    type = None  # set by subclasses: 'ipvpn', 'evpn', etc.
    afi = None
    safi = None

    @log_decorator.log
    def __init__(self, vpn_manager, dataplane_driver,
                 external_instance_id, instance_id, import_rts, export_rts,
                 gateway_ip, mask, readvertise, attract_traffic, fallback=None,
                 **kwargs):

        self.manager = vpn_manager

        self.instance_type = self.__class__.__name__
        self.instance_id = instance_id

        threading.Thread.__init__(self)
        self.setDaemon(True)

        if dataplane_driver.ecmp_support:
            compare_routes = tracker_worker.compare_ecmp
        else:
            compare_routes = tracker_worker.compare_no_ecmp

        tracker_worker.TrackerWorker.__init__(
            self,
            self.manager.bgp_manager, "%s-%d" % (self.instance_type,
                                                 self.instance_id),
            compare_routes)

        lg.LookingGlassLocalLogger.__init__(self,
                                            "%s-%d" % (self.instance_type,
                                                       self.instance_id))
        self.lock = threading.RLock()

        self.import_rts = import_rts
        self.export_rts = export_rts
        self.external_instance_id = external_instance_id
        self.gateway_ip = gateway_ip
        self.mask = mask

        self.fallback = None

        self.afi = self.__class__.afi
        self.safi = self.__class__.safi

        self.dp_driver = dataplane_driver

        if 'vni' in kwargs:
            self.instance_label = kwargs.pop('vni')
            self.forced_vni = True
        else:
            self.instance_label = self.manager.label_allocator.get_new_label(
                "Incoming traffic for %s %d" % (self.instance_type,
                                                self.instance_id))
            self.forced_vni = False

        self.instance_rd = self.manager.rd_allocator.get_new_rd(
            "Default route distinguisher for %s %d" % (self.instance_type,
                                                       self.instance_id))

        self.localport_data = dict()

        # One local port -> set of endpoints (MAC and IP addresses tuple)
        self.localport_2_endpoints = collections.defaultdict(set)
        # One endpoint (MAC and IP addresses tuple) -> One route distinguisher
        self.endpoint_2_rd = dict()
        # endpoint (MAC and IP addresses tuple) -> route entry
        self.endpoint_2_route = dict()
        # One MAC address -> One local port
        self.mac_2_localport_data = dict()
        # One IP address ->  Multiple MAC address
        self.ip_address_2_mac = collections.defaultdict(set)

        # One endpoint (MAC and IP addresses tuple) -> BGP local_pref
        self.endpoint_2_lp = dict()

        # Redirected instances list from which traffic is attracted (based on
        # FlowSpec 5-tuple classification)
        self.redirected_instances = set()

        self.dataplane = self.dp_driver.initialize_dataplane_instance(
            self.instance_id, self.external_instance_id,
            self.gateway_ip, self.mask, self.instance_label, **kwargs)

        for rt in self.import_rts:
            self._subscribe(self.afi, self.safi, rt)
            # Subscribe to FlowSpec routes
            # FIXME(tmorin): this maybe isn't applicable yet to E-VPN yet
            self._subscribe(self.afi, exa.SAFI.flow_vpn, rt)

        if readvertise:
            self.readvertise = True
            try:
                self.readvertise_to_rts = readvertise['to_rt']
            except KeyError:
                raise exc.APIException("'readvertise' specified with no "
                                       "'to_rt'")
            self.readvertise_from_rts = readvertise.get('from_rt', [])
            self.log.debug("readvertise enabled, from RT:%s, to %s",
                           self.readvertise_from_rts, self.readvertise_to_rts)
            for rt in self.readvertise_from_rts:
                self._subscribe(self.afi, self.safi, rt)
        else:
            self.log.debug("readvertise not enabled")
            self.readvertise = False

        self.attract_static_dest_prefixes = None

        if (attract_traffic and (self.readvertise or
                                 attract_traffic.get('to_rt'))):
            # Convert route target string to RouteTarget dictionary
            attract_to_rts = attract_traffic.get('to_rt')

            if attract_to_rts:
                converted_to_rts = (
                    utils.convert_route_targets(attract_to_rts)
                )
                if self.readvertise:
                    if converted_to_rts != self.readvertise_to_rts:
                        raise exc.APIException("if both are set, then "
                                               "'attract_traffic/to_rt' and "
                                               "'readvertise/to_rt' have to "
                                               "be equal")
                else:
                    self.readvertise_to_rts = converted_to_rts

                try:
                    self.attract_static_dest_prefixes = (
                        attract_traffic['static_destination_prefixes']
                    )
                except KeyError:
                    raise exc.APIException("'attract_traffic/to_rt' specified "
                                           "without "
                                           "'static_destination_prefixes'")

            if len(self.readvertise_to_rts) != 1:
                raise exc.APIException("attract_traffic requires exactly one "
                                       "RT to be provided in "
                                       "'readvertise/to_rt' and "
                                       "'attract_traffic/to_rt'")
            self.attract_traffic = True
            self.attract_rts = attract_traffic['redirect_rts']
            try:
                self.attract_classifier = attract_traffic['classifier']
            except KeyError:
                raise exc.APIException("'attract_traffic' specified with no "
                                       "'classifier'")
            self.log.debug("Attract traffic enabled with RT: %s and "
                           "classifier: %s", self.attract_rts,
                           self.attract_classifier)
        else:
            self.log.debug("attract traffic not enabled")
            self.attract_traffic = False

        self.dataplane.update_fallback(fallback)

    @utils.synchronized
    @log_decorator.log
    def stop(self):
        self.stop_event_loop()

        if self.dataplane.needs_cleanup_assist():
            self.log.debug("Dataplane driver needs cleanup assistance")
            self.synthesize_withdraw_all()

        self.dataplane.cleanup()
        if not self.forced_vni:
            self.manager.label_allocator.release(self.instance_label)

        # this makes sure that the thread will be stopped, and any remaining
        # routes/subscriptions are released:
        tracker_worker.TrackerWorker.stop(self)

    @utils.synchronized
    @log_decorator.log
    def stop_if_empty(self):
        self.log.debug("localport_2_endpoints: %s", self.localport_2_endpoints)
        if self.is_empty():
            self.stop()
            return True

        return False

    def is_empty(self):
        return not self.localport_2_endpoints

    def has_enpoint(self, linuxif):
        return self.localport_2_endpoints.get(linuxif) is not None

    def has_only_one_endpoint(self):
        return (len(self.localport_2_endpoints) == 1 and
                len(six.next(six.itervalues(self.localport_2_endpoints))) == 1)

    @log_decorator.log
    def update_route_targets(self, new_import_rts, new_export_rts):
        added_import_rt = set(new_import_rts) - set(self.import_rts)
        removed_import_rt = set(self.import_rts) - set(new_import_rts)

        self.log.debug("%s %d - Added Import RTs: %s",
                       self.instance_type, self.instance_id, added_import_rt)
        self.log.debug("%s %d - Removed Import RTs: %s",
                       self.instance_type, self.instance_id, removed_import_rt)

        # Unregister from BGP with these route targets
        for rt in removed_import_rt:
            self._unsubscribe(self.afi, self.safi, rt)
            self._unsubscribe(self.afi, exa.SAFI.flow_vpn, rt)

        # Update import and export route targets
        # (needs to be done before subscribe or we get a race where
        # VRF._imported rejects route that it's supposed to use)
        self.import_rts = new_import_rts

        # Register to BGP with these route targets
        for rt in added_import_rt:
            self._subscribe(self.afi, self.safi, rt)
            self._subscribe(self.afi, exa.SAFI.flow_vpn, rt)

        # Re-advertise all routes with new export RTs
        self.log.debug("Exports RTs: %s -> %s", self.export_rts,
                       new_export_rts)
        if frozenset(new_export_rts) != frozenset(self.export_rts):
            self.log.debug("Will re-export routes with new RTs")
            self.export_rts = new_export_rts
            # FIXME: we should only update the routes that
            # are routes of ports plugged to the VPN instance,
            # not all routes which would wrongly include
            # routes that we re-advertise between RTs
            for route_entry in self.get_route_entries():
                self.log.info("Re-advertising route %s with updated RTs (%s)",
                              route_entry.nlri, new_export_rts)

                updated_route_entry = engine.RouteEntry(
                    route_entry.nlri,
                    None,
                    copy.copy(route_entry.attributes))
                # reset the route_targets
                # will RTs originally present in route_entry.attributes
                updated_route_entry.set_route_targets(self.export_rts)

                self.log.debug("   updated route: %s", updated_route_entry)

                self._advertise_route(updated_route_entry)

    def update_fallback(self, fallback):
        if self.fallback != fallback and fallback is not None:
            self.log.info("update fallback: %s", fallback)
            self.fallback = fallback
            self.dataplane.update_fallback(fallback)

    def _parse_ipaddress_prefix(self, ip_address_prefix):
        ip_address = ""
        mask = 0
        try:
            net = netaddr.IPNetwork(ip_address_prefix)
            (ip_address, mask) = (str(net.ip), net.prefixlen)
        except netaddr.core.AddrFormatError:
            raise exc.APIException("Bogus IP prefix: %s" % ip_address_prefix)

        return (ip_address, mask)

    def _gen_encap_extended_communities(self):
        ecommunities = exa.extcoms.ExtendedCommunities()
        for encap in self.dp_driver.supported_encaps():
            if not isinstance(encap, exa.Encapsulation):
                raise Exception("dp_driver.supported_encaps() should "
                                "return a list of Encapsulation objects (%s)",
                                type(encap))

            if encap != exa.Encapsulation(
                    exa.Encapsulation.Type.DEFAULT):
                ecommunities.communities.append(encap)
        # FIXME: si DEFAULT + xxx => adv MPLS
        return ecommunities

    @abc.abstractmethod
    def generate_vif_bgp_route(self, mac_address, ip_prefix, plen, label, rd):
        '''returns a RouteEntry'''
        pass

    def synthesize_vif_bgp_route(self, mac_address, ip_prefix, plen, label,
                                 lb_consistent_hash_order,
                                 route_distinguisher=None,
                                 local_pref=None):
        rd = route_distinguisher if route_distinguisher else self.instance_rd
        route_entry = self.generate_vif_bgp_route(mac_address, ip_prefix, plen,
                                                  label, rd)
        assert isinstance(route_entry, engine.RouteEntry)

        route_entry.attributes.add(self._gen_encap_extended_communities())
        route_entry.set_route_targets(self.export_rts)

        ecommunities = exa.ExtendedCommunities()
        ecommunities.communities.append(
            exa.ConsistentHashSortOrder(lb_consistent_hash_order))
        route_entry.attributes.add(ecommunities)

        route_entry.attributes.add(exa.LocalPreference(local_pref
                                                       or DEFAULT_LOCAL_PREF))

        self.log.debug("Synthesized Vif route entry: %s", route_entry)
        return route_entry

    def synthesize_redirect_bgp_route(self, rules):
        self.log.info("synthesize_redirect_bgp_route called for rules %s",
                      rules)
        nlri = flowspec.FlowRouteFactory(self.afi, self.instance_rd)
        for rule in rules:
            nlri.add(rule)

        route_entry = engine.RouteEntry(nlri)

        assert isinstance(route_entry, engine.RouteEntry)

        ecommunities = exa.ExtendedCommunities()

        # checked at __init__:
        assert len(self.readvertise_to_rts) == 1
        rt = self.readvertise_to_rts[0]
        ecommunities.communities.append(
            exa.TrafficRedirect(exa.ASN(int(rt.asn)), int(rt.number))
        )

        route_entry.attributes.add(ecommunities)
        route_entry.set_route_targets(self.attract_rts)

        self.log.debug("Synthesized redirect route entry: %s", route_entry)
        return route_entry

    @classmethod
    def validate_convert_params(cls, params, also_mandatory=()):

        for param in ('vpn_instance_id', 'mac_address', 'ip_address',
                      'local_port') + also_mandatory:
            if param not in params:
                raise exc.APIMissingParameterException(param)

        # if local_port is not a dict, then assume it designates a linux
        # interface
        if (isinstance(params['local_port'], six.string_types) or
                isinstance(params['local_port'], six.text_type)):
            params['local_port'] = {'linuxif': params['local_port']}

        for param in ('import_rt', 'export_rt'):
            if param not in params:
                continue

            # if import_rt or export_rt are strings, convert them into lists
            if (isinstance(params[param], six.string_types) or
                    isinstance(params[param], six.text_type)):
                try:
                    params[param] = re.split(',+ *', params[param])
                except Exception:
                    raise exc.APIException("Unable to parse RT string into "
                                           " a list: '%s'" % params[param])
            # remove duplicates
            params[param] = list(set(params[param]))

        if not ('linuxif' in params['local_port'] or
                'evpn' in params['local_port']):
            raise exc.APIException("Mandatory key is missing in local_port "
                                   "parameter (linuxif, or evpn)")

        # Verify and format IP address with prefix if necessary
        if re.match(r'([12]?\d?\d\.){3}[12]?\d?\d\/[123]?\d',
                    params['ip_address']):
            params['ip_address_prefix'] = params['ip_address']
        elif re.match(r'([12]?\d?\d\.){3}[12]?\d?\d', params['ip_address']):
            params['ip_address_prefix'] = params['ip_address'] + "/32"
        else:
            raise exc.MalformedIPAddress(params['ip_address'])

        # NOTE(tmorin): improve the IP check above and validate MAC address
        # format

        if not isinstance(params.get('advertise_subnet', False), bool):
            raise exc.APIException("'advertise_subnet' must be a boolean")

    @classmethod
    def translate_api_internal(cls, params):
        # some API parameters have different internal names
        _TRANSLATE_API_TO_INTERNAL = {
            'vpn_instance_id': 'external_instance_id',
            'local_port': 'localport',
            'import_rt': 'import_rts',  # API name is singular, hence wrong...
            'export_rt': 'export_rts',  # API name is singular, hence wrong...
        }

        for api_param_name in list(params):
            internal_name = _TRANSLATE_API_TO_INTERNAL.get(api_param_name)
            if internal_name:
                params[internal_name] = params.pop(api_param_name)

    @classmethod
    def validate_convert_attach_params(cls, params):
        cls.validate_convert_params(
            params,
            also_mandatory=('import_rt', 'export_rt')
            )

        params['advertise_subnet'] = params.get('advertise_subnet', False)
        params['lb_consistent_hash_order'] = params.get(
            'lb_consistent_hash_order', 0)
        params['vni'] = params.get('vni', 0)

        cls.translate_api_internal(params)

    @classmethod
    def validate_convert_detach_params(cls, params):
        cls.validate_convert_params(params)
        cls.translate_api_internal(params)

    def _rd_for_endpoint(self, endpoint, message):
        # endpoint is a (mac, ip_address_prefix) tuple
        rd = self.endpoint_2_rd.get(endpoint)
        if not rd:
            rd = self.manager.rd_allocator.get_new_rd(message)
            self.endpoint_2_rd[endpoint] = rd
        return rd

    @utils.synchronized
    @log_decorator.log_info
    def vif_plugged(self, mac_address, ip_address_prefix, localport,
                    advertise_subnet=False,
                    lb_consistent_hash_order=0, local_pref=None):
        linuxif = localport['linuxif']
        endpoint = (mac_address, ip_address_prefix)
        # Check if this port has already been plugged
        # - Verify port informations consistency
        if mac_address in self.mac_2_localport_data:
            self.log.debug("MAC address already plugged, checking port "
                           "consistency")
            pdata = self.mac_2_localport_data[mac_address]

            if pdata.get("port_info") != localport:
                raise exc.APIException("Port information is not consistent. "
                                       "MAC address cannot be bound to two "
                                       "different ports. Previous plug for "
                                       "port %s (%s != %s)" %
                                       (linuxif, pdata.get("port_info"),
                                        localport))

        try:
            # Parse address/mask
            (ip_prefix, plen) = self._parse_ipaddress_prefix(ip_address_prefix)

            if not advertise_subnet and plen != 32:
                self.log.debug("Using /32 instead of /%d", plen)
                plen = 32

            # - Verify (MAC address, IP address) tuple consistency
            refresh_only = False
            if ip_address_prefix in self.ip_address_2_mac and plen == 32:
                if mac_address not in self.ip_address_2_mac[ip_address_prefix]:
                    raise exc.APIException("Inconsistent endpoint info: %s "
                                           "already bound to a MAC address "
                                           "different from %s" %
                                           (ip_address_prefix, mac_address))
                else:
                    LOG.debug("IP/MAC already plugged, only updating route")
                    refresh_only = True
                    return

            self.log.debug("Plugging port (%s)", ip_prefix)

            pdata = self.mac_2_localport_data.get(mac_address, dict())
            if not pdata:
                pdata['label'] = self.manager.label_allocator.get_new_label(
                    "Incoming traffic for %s %d, interface %s"
                    ", endpoint %s/%s" %
                    (self.instance_type, self.instance_id,
                     linuxif, mac_address, ip_address_prefix)
                )
                pdata["port_info"] = localport
                pdata["lb_consistent_hash_order"] = lb_consistent_hash_order

            endpoint_rd = self._rd_for_endpoint(
                endpoint,
                "Route distinguisher for %s %d, interface %s, "
                "endpoint %s/%s" % (self.instance_type, self.instance_id,
                                    linuxif, mac_address,
                                    ip_address_prefix)
            )

            rd = self.instance_rd if plen == 32 else endpoint_rd

            if not refresh_only:
                # Call driver to setup the dataplane for incoming traffic
                self.dataplane.vif_plugged(mac_address, ip_prefix,
                                           localport, pdata['label'])

            self.log.info("Synthesizing and advertising BGP route for VIF %s "
                          "endpoint (%s, %s/%d)", linuxif,
                          mac_address, ip_prefix, plen)
            route_entry = self.synthesize_vif_bgp_route(
                mac_address, ip_prefix, plen,
                pdata['label'], lb_consistent_hash_order, rd, local_pref)

            self._advertise_route(route_entry)

            self.endpoint_2_route[endpoint] = route_entry
            self.endpoint_2_rd[endpoint] = endpoint_rd
            self.localport_2_endpoints[linuxif].add(endpoint)
            self.endpoint_2_lp[endpoint] = local_pref
            self.mac_2_localport_data[mac_address] = pdata

            self.ip_address_2_mac[ip_address_prefix].add(mac_address)

        except Exception as e:
            self.log.error("Error in vif_plugged: %s", e)
            if linuxif in self.localport_2_endpoints:
                self.localport_2_endpoints[linuxif].discard(endpoint)
                if not self.localport_2_endpoints[linuxif]:
                    del self.localport_2_endpoints[linuxif]
            if mac_address in self.mac_2_localport_data:
                del self.mac_2_localport_data[mac_address]
            if ip_address_prefix in self.ip_address_2_mac:
                self.ip_address_2_mac[ip_address_prefix].discard(mac_address)

            raise

        self.log.info("localport_2_endpoints: %s", self.localport_2_endpoints)
        self.log.info("endpoint_2_rd: %s", self.endpoint_2_rd)
        self.log.info("mac_2_localport_data: %s", self.mac_2_localport_data)
        self.log.info("ip_address_2_mac: %s", self.ip_address_2_mac)

    @utils.synchronized
    @log_decorator.log_info
    def vif_unplugged(self, mac_address, ip_address_prefix,
                      lb_consistent_hash_order=0):
        # NOTE(tmorin): move this as a vif_unplugged_precheck, so that
        # in ipvpn.VRF this is done before readvertised route withdrawal
        endpoint = (mac_address, ip_address_prefix)
        # Verify port and endpoint (MAC address, IP address) tuple consistency
        pdata = self.mac_2_localport_data.get(mac_address)
        if (not pdata or
                (ip_address_prefix in self.ip_address_2_mac and
                 mac_address not in self.ip_address_2_mac[ip_address_prefix])
                or endpoint not in self.endpoint_2_rd):
            self.log.error("vif_unplugged called for endpoint (%s, %s), but "
                           "no consistent informations or was not plugged yet",
                           *endpoint)
            raise exc.APIException("Inconsistent endpoint (%s, %s) info "
                                   "or endpoint wasn't plugged yet, "
                                   "cannot unplug" % endpoint)

        # Finding label and local port informations
        label = pdata.get('label')
        localport = pdata.get('port_info')
        linuxif = localport['linuxif']
        if not label or not localport:
            self.log.error("vif_unplugged called for endpoint (%s, %s), but "
                           "port data (%s, %s) is incomplete",
                           mac_address, ip_address_prefix, label, localport)
            raise Exception("Inconsistent informations for port, bug ?")

        if linuxif in self.localport_2_endpoints:
            # Parse address/mask
            (ip_prefix, _) = self._parse_ipaddress_prefix(ip_address_prefix)

            last_endpoint = len(self.localport_2_endpoints[linuxif]) <= 1

            self.log.info("Withdrawing BGP route for VIF %s endpoint "
                          "(%s, %s)", linuxif, mac_address, ip_address_prefix)

            self._withdraw_route(self.endpoint_2_route.pop(endpoint))

            # Unplug endpoint from data plane
            self.dataplane.vif_unplugged(
                mac_address, ip_prefix, localport, label, last_endpoint)

            # Forget data for this port if last endpoint
            if last_endpoint:
                self.log.info("Last endpoint, freeing label %s", label)
                # Free label to the allocator
                self.manager.label_allocator.release(label)

                del self.localport_2_endpoints[linuxif]
            else:
                self.localport_2_endpoints[linuxif].remove(endpoint)

            # Free route distinguisher to the allocator
            self.manager.rd_allocator.release(self.endpoint_2_rd.pop(endpoint))

            if not last_endpoint:
                if not any([ep[0] == mac_address
                            for ep
                            in self.localport_2_endpoints[linuxif]]
                           ):
                    del self.mac_2_localport_data[mac_address]
            else:
                del self.mac_2_localport_data[mac_address]

            self.ip_address_2_mac[ip_address_prefix].discard(mac_address)

            if not self.ip_address_2_mac[ip_address_prefix]:
                del self.ip_address_2_mac[ip_address_prefix]
        else:
            self.log.error("vif_unplugged called for endpoint {%s, %s}, but"
                           " port data is incomplete", mac_address,
                           ip_address_prefix)
            raise Exception("bagpipe-bgp bug, check its logs")

        self.log.info("localport_2_endpoints: %s", self.localport_2_endpoints)
        self.log.info("mac_2_localport_data: %s", self.mac_2_localport_data)
        self.log.info("ip_address_2_mac: %s", self.ip_address_2_mac)

    @utils.synchronized
    def register_redirected_instance(self, instance_id):
        self.redirected_instances.add(instance_id)

    @utils.synchronized
    def unregister_redirected_instance(self, instance_id):
        self.redirected_instances.remove(instance_id)

    @utils.synchronized
    @log_decorator.log
    def stop_if_no_redirected_instance(self):
        self.log.debug("redirected_instances: %s", self.redirected_instances)
        if not self.redirected_instances:
            self.stop()
            return True

        return False

    @log_decorator.log
    def start_redirect_traffic(self, redirect_rt, rules):
        self.log.debug("Start redirecting traffic to VPN instance importing "
                       "route target %s based on rules %s", redirect_rt, rules)
        # Create redirection instance if first FlowSpec route for this
        # redirect route target
        redirect_instance = self.manager.redirect_traffic_to_vpn(
            self.external_instance_id, self.type, redirect_rt
        )
        # Create traffic classifier from FlowSpec rules
        classifier = TrafficClassifier()
        classifier.map_redirect_rules_2_traffic_classifier(rules)

        self.dataplane.add_dataplane_for_traffic_classifier(
            classifier,
            redirect_instance.instance_id)

        if not hasattr(self, 'redirect_rt_2_classifiers'):
            # One redirect route target -> Multiple traffic classifiers (One
            # per prefix)
            # Can be inverted to one traffic classifier -> Multiple redirect
            # route targets
            self.redirect_rt_2_classifiers = collections.defaultdict(set)

        self.redirect_rt_2_classifiers[redirect_rt].add(classifier)

    @log_decorator.log
    def stop_redirect_traffic(self, redirect_rt, rules):
        self.log.debug("Stop redirecting traffic to VPN instance importing "
                       "route target %s based on rules %s", redirect_rt, rules)
        # Create traffic classifier from FlowSpec rule
        classifier = TrafficClassifier()
        classifier.map_redirect_rules_2_traffic_classifier(rules)

        if (redirect_rt in self.redirect_rt_2_classifiers and
                classifier in self.redirect_rt_2_classifiers[redirect_rt]):
            self.redirect_rt_2_classifiers[redirect_rt].remove(classifier)

            if not utils.invert_dict_of_sets(
                    self.redirect_rt_2_classifiers)[classifier]:
                self.dataplane.remove_dataplane_for_traffic_classifier(
                    classifier)

            if not self.redirect_rt_2_classifiers[redirect_rt]:
                self.manager.stop_redirect_to_vpn(
                    self.external_instance_id, self.type, redirect_rt
                )
                del self.redirect_rt_2_classifiers[redirect_rt]
        else:
            self.log.error("stop_redirect_traffic called for redirect route "
                           "target %s and classifier %s, but doesn't exist",
                           redirect_rt, classifier)
            raise Exception("bagpipe-bgp bug, check its logs")

    def _check_encaps(self, route):
        '''check that encaps of a route

        returns a list of encaps supported by both the dataplane driver and the
        advertized route (based on BGP Encapsulation community)

        logs a warning if there is no common encap
        '''
        adv_encaps = None
        try:
            adv_encaps = route.ecoms(exa.Encapsulation)
            self.log.debug("Advertized Encaps: %s", adv_encaps)
        except KeyError:
            self.log.debug("no encap advertized, let's use default")

        if not adv_encaps:
            adv_encaps = [exa.Encapsulation(
                exa.Encapsulation.Type.DEFAULT)]

        good_encaps = set(adv_encaps) & set(
            self.dp_driver.supported_encaps())

        if not good_encaps:
            self.log.warning("No encap supported by dataplane driver for route"
                             " %s, advertized: %s, dataplane supports: {%s}",
                             route, adv_encaps,
                             ", ".join([repr(encap) for encap in
                                        self.dp_driver.supported_encaps()]
                                       ))

        return good_encaps

    def _skip_route_removal(self, last):
        '''check if a route withdraw should be skipped

        returns true if the removal of the route should be skipped, based
        whether or not the route removed is the last one and depending on
        the desired behavior for the dataplane driver
        '''
        if last:
            # never skip the last route
            return False

        # if the driver supports ECMP, then it needs to see all the route
        # withdraws
        return not self.dp_driver.ecmp_support

    # Callbacks for BGP route updates (TrackerWorker) ########################

    @utils.synchronized
    @log_decorator.log
    def new_best_route(self, entry, new_route):
        pass

    @utils.synchronized
    @log_decorator.log
    def best_route_removed(self, entry, old_route, last):
        pass

    # Looking Glass ####

    def get_lg_map(self):
        return {
            "instance_type":         (lg.VALUE, self.instance_type),
            "external_instance_id":  (lg.VALUE, self.external_instance_id),
            "dataplane":             (lg.DELEGATE, self.dataplane),
            "route_targets":         (lg.SUBITEM, self.get_rts),
            "gateway_ip":            (lg.VALUE, self.gateway_ip),
            "subnet_mask":           (lg.VALUE, self.mask),
            "instance_dataplane_id": (lg.VALUE, self.instance_label),
            "ports":                 (lg.SUBTREE, self.get_lg_local_port_data),
            "readvertise":           (lg.SUBITEM, self.get_lg_readvertise),
            "attract_traffic":       (lg.SUBITEM, self.get_lg_attract_traffic),
            "fallback":              (lg.VALUE, self.fallback)
        }

    def get_lg_local_port_data(self, path_prefix):
        r = {}
        for (port, endpoints) in self.localport_2_endpoints.items():
            eps = []
            for endpoint in endpoints:
                mac, ip = endpoint
                eps.append({
                    'label': self.mac_2_localport_data[mac]['label'],
                    'mac_address': mac,
                    'ip_address': ip,
                    'local_pref': self.endpoint_2_lp.get(endpoint),
                    'rd': repr(self.endpoint_2_rd[endpoint])
                })

            r[port] = {
                'endpoints': eps
            }
        return r

    def get_rts(self):
        return {
            "import": [repr(rt) for rt in self.import_rts],
            "export": [repr(rt) for rt in self.export_rts]
        }

    def get_lg_readvertise(self):
        r = {}
        if self.readvertise:
            r = {
                'from': [repr(rt) for rt in self.readvertise_from_rts],
                'to': [repr(rt) for rt in self.readvertise_to_rts]
            }
        return r

    def get_lg_attract_traffic(self):
        r = {}
        if self.attract_traffic:
            r = {
                'redirect_rts': [repr(rt) for rt in self.attract_rts],
                'classifier': self.attract_classifier,
            }

            if not hasattr(self, 'attract_static_dest_prefixes'):
                return r

            r.update({
                'to': [repr(rt) for rt in self.readvertise_to_rts],
                'static_destination_prefixes':
                    self.attract_static_dest_prefixes
            })

        return r
