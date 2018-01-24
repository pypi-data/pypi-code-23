# Copyright (c) 2015 Orange.
# All Rights Reserved.
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

import copy

import mock

from oslo_utils import uuidutils

from networking_bagpipe.agent import bagpipe_bgp_agent
from networking_bagpipe.agent.bgpvpn import constants as bgpvpn_const
from networking_bagpipe.bagpipe_bgp import constants as bbgp_const

from neutron.plugins.ml2.drivers.linuxbridge.agent.common \
    import constants as lnx_agt_constants
from neutron.plugins.ml2.drivers.linuxbridge.agent \
    import linuxbridge_neutron_agent as lnx_agt
from neutron.plugins.ml2.drivers.openvswitch.agent.common \
    import constants as ovs_agt_constants
from neutron.plugins.ml2.drivers.openvswitch.agent \
    import ovs_agent_extension_api as ovs_ext_agt
from neutron.plugins.ml2.drivers.openvswitch.agent import vlanmanager

from neutron.tests import base
from neutron.tests.unit.plugins.ml2.drivers.openvswitch.agent \
    import ovs_test_base


PATCH_TUN_TO_MPLS_OFPORT = 1
PATCH_TUN_OFPORTS = [PATCH_TUN_TO_MPLS_OFPORT]

PATCH_INT_TO_MPLS_OFPORT = 5
PATCH_INT_OFPORTS = [PATCH_INT_TO_MPLS_OFPORT]

PATCH_MPLS_TO_TUN_OFPORT = 2
PATCH_MPLS_TO_INT_OFPORT = 6
PATCH_MPLS_OFPORTS = [PATCH_MPLS_TO_TUN_OFPORT, PATCH_MPLS_TO_INT_OFPORT]

PORT10_ID = uuidutils.generate_uuid()
PORT10 = {'id': PORT10_ID,
          'mac_address': '00:00:de:ad:be:ef',
          'ip_address': '10.0.0.2'}

PORT11 = {'id': uuidutils.generate_uuid(),
          'mac_address': '00:00:de:ad:f0:0d',
          'ip_address': '10.0.0.3'}

NETWORK1 = {'id': uuidutils.generate_uuid(),
            'gateway_ip': '10.0.0.1'}

PORT20 = {'id': uuidutils.generate_uuid(),
          'mac_address': '00:00:de:ad:be:ef',
          'ip_address': '20.0.0.2'}

PORT21 = {'id': uuidutils.generate_uuid(),
          'mac_address': '00:00:de:ad:f0:0d',
          'ip_address': '20.0.0.3'}

NETWORK2 = {'id': uuidutils.generate_uuid(),
            'gateway_ip': '20.0.0.1'}

ROUTER1 = {'id': uuidutils.generate_uuid()}

port_2_net = {
    PORT10['id']: NETWORK1,
    PORT11['id']: NETWORK1,
    PORT20['id']: NETWORK2,
    PORT21['id']: NETWORK2,
}

LOCAL_VLAN_MAP = {
    NETWORK1['id']: 31,
    NETWORK2['id']: 52
}

BAGPIPE_L2_RT1 = {'import_rt': 'BAGPIPE_L2:1',
                  'export_rt': 'BAGPIPE_L2:1'}

BAGPIPE_L2_RT2 = {'import_rt': 'BAGPIPE_L2:2',
                  'export_rt': 'BAGPIPE_L2:2'}

BGPVPN_L2_RT10 = {'route_targets': ['BGPVPN_L2:10'],
                  'import_targets': [],
                  'export_targets': []
                  }

BGPVPN_L2_RT20 = {'route_targets': ['BGPVPN_L2:20'],
                  'import_targets': [],
                  'export_targets': []
                  }

BGPVPN_L3_RT100 = {'route_targets': ['BGPVPN_L3:100'],
                   'import_targets': [],
                   'export_targets': []
                   }

BGPVPN_L3_RT200 = {'route_targets': ['BGPVPN_L3:200'],
                   'import_targets': [],
                   'export_targets': []
                   }

TEST_VNI = 411


class DummyPort(object):
    def __init__(self, network, port, bgpvpn_port=False,
                 evpn=None, ipvpn=None):
        self.id = port['id']
        self.network_id = network['id']
        self.mac_address = port['mac_address']
        self.ip_address = port['ip_address']
        self.gateway_ip = network['gateway_ip']

        if bgpvpn_port:
            if evpn:
                self.l2vpn = copy.deepcopy(evpn)

            if ipvpn:
                self.l3vpn = copy.deepcopy(ipvpn)
        else:
            if evpn:
                self.evpn = copy.deepcopy(evpn)

            if ipvpn:
                self.ipvpn = copy.deepcopy(ipvpn)


class DummyVif(object):
    def __init__(self, ofport, port_name):
        self.ofport = ofport
        self.port_name = port_name


class DummyBGPVPN(object):
    def __init__(self, network, l2vpn=None, l3vpn=None, gateway_mac=None):
        self.id = uuidutils.generate_uuid()
        self.network_id = network['id']

        if l2vpn:
            self.l2vpn = copy.deepcopy(l2vpn)

        if l3vpn:
            self.l3vpn = copy.deepcopy(l3vpn)

        if gateway_mac:
            self.gateway_mac = gateway_mac


class RTList(list):

    def __eq__(self, other):
        return set(self) == set(other)


class BaseTestAgentExtension(object):

    agent_extension_class = None

    DUMMY_VIF10 = None
    DUMMY_VIF11 = None
    DUMMY_VIF20 = None
    DUMMY_VIF21 = None

    def setUp(self):
        self.mocked_bagpipe_agent = mock.Mock(
            spec=bagpipe_bgp_agent.BaGPipeBGPAgent
        )
        self.mocked_bagpipe_agent.do_port_plug = mock.Mock()
        self.mocked_bagpipe_agent.do_port_plug_refresh = mock.Mock()

        patcher = mock.patch('networking_bagpipe.agent.bagpipe_bgp_agent.'
                             'BaGPipeBGPAgent.get_instance',
                             return_value=self.mocked_bagpipe_agent)
        patcher.start()
        self.addCleanup(patcher.stop)

        self.agent_ext = self.agent_extension_class()
        self.connection = mock.Mock()

    def _port_data(self, port, delete=False):
        data = {
            'port_id': port['id']
        }
        if not delete:
            data.update({
                'port_id': port['id'],
                'network_id': port_2_net[port['id']]['id'],
                'segmentation_id': TEST_VNI,
                'network_type': 'vxlan',
                'device_owner': 'compute:None',
                'mac_address': port['mac_address'],
                'fixed_ips': [
                    {
                        'ip_address': port['ip_address'],
                    }
                ]
            })
        return data

    def _get_expected_local_port(self, bbgp_vpn_type, network_id, port_id,
                                 detach=False):
        raise NotImplementedError

    def _check_network_info(self, network_id, expected_size,
                            vpn_type=None, vpn_rts=None):
        if expected_size == 0:
            self.assertNotIn(network_id, self.agent_ext.networks_info,
                             "Network %s expected to have no ports left"
                             % network_id)
        else:
            self.assertIn(network_id, self.agent_ext.networks_info)
            network_info = self.agent_ext.networks_info[network_id]
            self.assertEqual(len(network_info.ports), expected_size,
                             "Network ports size not as expected")

            if vpn_type and vpn_rts:
                service_infos = network_info.service_infos
                self.assertIn(vpn_type, service_infos,
                              "No %s details found for network %s" %
                              (vpn_type, network_id))

                self.assertEqual(vpn_rts, service_infos[vpn_type],
                                 "%s details not matching %s for network %s" %
                                 (vpn_type, vpn_rts, network_id))


class BaseTestLinuxBridgeAgentExtension(base.BaseTestCase,
                                        BaseTestAgentExtension):

    driver_type = lnx_agt_constants.EXTENSION_DRIVER_TYPE

    def setUp(self):
        base.BaseTestCase.setUp(self)
        BaseTestAgentExtension.setUp(self)

        agent_extension_api = mock.Mock()
        self.agent_ext.consume_api(agent_extension_api)
        self.agent_ext.initialize(self.connection,
                                  lnx_agt_constants.EXTENSION_DRIVER_TYPE)

    def _get_expected_local_port(self, bbgp_vpn_type, network_id, port_id,
                                 detach=False):
        linuxbr = lnx_agt.LinuxBridgeManager.get_bridge_name(network_id)

        if bbgp_vpn_type == bbgp_const.EVPN:
            r = {
                'linuxbr': linuxbr,
                'local_port': {
                    'linuxif': lnx_agt.LinuxBridgeManager.get_tap_device_name(
                        port_id)
                }
            }
            if detach:
                del r['linuxbr']
            return r
        else:  # if bbgp_const.IPVPN:
            return {
                'local_port': {
                    'linuxif': linuxbr
                }
            }


class BaseTestOVSAgentExtension(ovs_test_base.OVSOFCtlTestBase,
                                BaseTestAgentExtension):

    driver_type = ovs_agt_constants.EXTENSION_DRIVER_TYPE

    DUMMY_VIF10 = DummyVif(10, 'VIF10')
    DUMMY_VIF11 = DummyVif(11, 'VIF11')
    DUMMY_VIF20 = DummyVif(20, 'VIF20')
    DUMMY_VIF21 = DummyVif(21, 'VIF21')

    def setUp(self):
        ovs_test_base.OVSOFCtlTestBase.setUp(self)
        BaseTestAgentExtension.setUp(self)

        int_br = self.br_int_cls("br-int")
        int_br.add_patch_port = mock.Mock(side_effect=PATCH_INT_OFPORTS)
        int_br.get_port_ofport = mock.Mock()
        int_br.add_flow = mock.Mock()
        int_br.delete_flows = mock.Mock()

        tun_br = self.br_tun_cls("br-tun")
        tun_br.add_patch_port = mock.Mock(side_effect=PATCH_TUN_OFPORTS)
        tun_br.get_port_ofport = mock.Mock()
        tun_br.add_flow = mock.Mock()
        tun_br.delete_flows = mock.Mock()

        agent_extension_api = ovs_ext_agt.OVSAgentExtensionAPI(int_br,
                                                               tun_br)
        self.agent_ext.consume_api(agent_extension_api)

        br_exists_patcher = mock.patch(
            'neutron.agent.common.ovs_lib.OVSBridge.bridge_exists',
            return_value=True)
        br_exists_patcher.start()
        self.addCleanup(br_exists_patcher.stop)

        add_patch_patcher = mock.patch('neutron.agent.common.ovs_lib.OVSBridge'
                                       '.add_patch_port',
                                       side_effect=PATCH_MPLS_OFPORTS*4)
        add_patch_patcher.start()
        self.addCleanup(add_patch_patcher.stop)

        self.agent_ext.initialize(self.connection,
                                  ovs_agt_constants.EXTENSION_DRIVER_TYPE)

        self.vlan_manager = vlanmanager.LocalVlanManager()
        for net_id, vlan in LOCAL_VLAN_MAP.items():
            try:
                self.vlan_manager.add(net_id, vlan, None, None, None)
            except vlanmanager.MappingAlreadyExists:
                pass

    def _get_expected_local_port(self, bbgp_vpn_type, network_id, port_id,
                                 detach=False):
        if bbgp_vpn_type == bbgp_const.IPVPN:
            vlan = self.vlan_manager.get(network_id).vlan
            r = dict(
                local_port=dict(
                    linuxif='%s:%s' % (bgpvpn_const.LINUXIF_PREFIX, vlan),
                    ovs=dict(plugged=True,
                             port_number=PATCH_MPLS_TO_TUN_OFPORT,
                             vlan=vlan)
                )
            )
            if detach:
                del r['local_port']['ovs']
            return r
        else:
            return {}
