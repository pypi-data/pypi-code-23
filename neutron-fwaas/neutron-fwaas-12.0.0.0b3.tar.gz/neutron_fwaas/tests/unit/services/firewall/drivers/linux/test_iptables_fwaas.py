# Copyright 2013 Dell Inc.
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
from neutron.tests import base
from neutron.tests.unit.api.v2 import test_base as test_api_v2

import neutron_fwaas.services.firewall.drivers.linux.iptables_fwaas as fwaas


_uuid = test_api_v2._uuid
FAKE_SRC_PREFIX = '10.0.0.0/24'
FAKE_DST_PREFIX = '20.0.0.0/24'
FAKE_PROTOCOL = 'tcp'
FAKE_SRC_PORT = 5000
FAKE_DST_PORT = 22
FAKE_FW_ID = 'fake-fw-uuid'
FW_LEGACY = 'legacy'


class IptablesFwaasTestCase(base.BaseTestCase):
    def setUp(self):
        super(IptablesFwaasTestCase, self).setUp()
        self.conntrack_driver = mock.Mock()
        self.conntrack_driver.initialize = mock.Mock()
        self.conntrack_driver.delete_entries = mock.Mock()
        self.conntrack_driver.flush_entries = mock.Mock()
        self.iptables_cls_p = mock.patch(
            'neutron.agent.linux.iptables_manager.IptablesManager')
        self.iptables_cls_p.start()
        self.firewall = fwaas.IptablesFwaasDriver()
        self.firewall.conntrack = self.conntrack_driver

    def _fake_rules_v4(self, fwid, apply_list):
        rule_list = []
        rule1 = {'enabled': True,
                 'action': 'allow',
                 'ip_version': 4,
                 'protocol': 'tcp',
                 'destination_port': '80',
                 'source_ip_address': '10.24.4.2',
                 'id': 'fake-fw-rule1'}
        rule2 = {'enabled': True,
                 'action': 'deny',
                 'ip_version': 4,
                 'protocol': 'tcp',
                 'destination_port': '22',
                 'id': 'fake-fw-rule2'}
        rule3 = {'enabled': True,
                 'action': 'reject',
                 'ip_version': 4,
                 'protocol': 'tcp',
                 'destination_port': '23',
                 'id': 'fake-fw-rule3'}
        ingress_chain = ('iv4%s' % fwid)[:11]
        egress_chain = ('ov4%s' % fwid)[:11]
        for router_info_inst in apply_list:
            v4filter_inst = router_info_inst.iptables_manager.ipv4['filter']
            v4filter_inst.chains.append(ingress_chain)
            v4filter_inst.chains.append(egress_chain)
        rule_list.append(rule1)
        rule_list.append(rule2)
        rule_list.append(rule3)
        return rule_list

    def _fake_firewall_no_rule(self):
        rule_list = []
        fw_inst = {'id': FAKE_FW_ID,
                   'admin_state_up': True,
                   'tenant_id': 'tenant-uuid',
                   'firewall_rule_list': rule_list}
        return fw_inst

    def _fake_firewall(self, rule_list):
        _rule_list = copy.deepcopy(rule_list)
        for rule in _rule_list:
            rule['position'] = str(_rule_list.index(rule))
        fw_inst = {'id': FAKE_FW_ID,
                   'admin_state_up': True,
                   'tenant_id': 'tenant-uuid',
                   'firewall_rule_list': _rule_list}
        return fw_inst

    def _fake_firewall_with_admin_down(self, rule_list):
        fw_inst = {'id': FAKE_FW_ID,
                   'admin_state_up': False,
                   'tenant_id': 'tenant-uuid',
                   'firewall_rule_list': rule_list}
        return fw_inst

    def _fake_apply_list(self, router_count=1, distributed=False,
            distributed_mode=None):
        apply_list = []
        while router_count > 0:
            iptables_inst = mock.Mock()
            if distributed is not None:
                router_inst = {'distributed': distributed}
            else:
                router_inst = {}
            v4filter_inst = mock.Mock()
            v6filter_inst = mock.Mock()
            v4filter_inst.chains = []
            v6filter_inst.chains = []
            iptables_inst.ipv4 = {'filter': v4filter_inst}
            iptables_inst.ipv6 = {'filter': v6filter_inst}
            router_info_inst = mock.Mock()
            router_info_inst.iptables_manager = iptables_inst
            router_info_inst.snat_iptables_manager = iptables_inst
            if distributed_mode == 'dvr':
                router_info_inst.dist_fip_count = 1
            router_info_inst.router = router_inst
            apply_list.append(router_info_inst)
            router_count -= 1
        return apply_list

    def _setup_firewall_with_rules(self, func, router_count=1,
            distributed=False, distributed_mode=None):
        apply_list = self._fake_apply_list(router_count=router_count,
            distributed=distributed, distributed_mode=distributed_mode)
        rule_list = self._fake_rules_v4(FAKE_FW_ID, apply_list)
        firewall = self._fake_firewall(rule_list)
        if distributed:
            if distributed_mode == 'dvr_snat':
                if_prefix = 'sg-+'
            if distributed_mode == 'dvr':
                if_prefix = 'rfp-+'
        else:
            if_prefix = 'qr-+'
            distributed_mode = 'legacy'
        func(distributed_mode, apply_list, firewall)
        invalid_rule = '-m state --state INVALID -j DROP'
        est_rule = '-m state --state RELATED,ESTABLISHED -j ACCEPT'
        rule1 = '-p tcp -s 10.24.4.2/32 -m tcp --dport 80 -j ACCEPT'
        rule2 = '-p tcp -m tcp --dport 22 -j DROP'
        rule3 = '-p tcp -m tcp --dport 23 -j REJECT'
        ingress_chain = 'iv4%s' % firewall['id']
        egress_chain = 'ov4%s' % firewall['id']
        bname = fwaas.iptables_manager.binary_name
        ipt_mgr_ichain = '%s-%s' % (bname, ingress_chain[:11])
        ipt_mgr_echain = '%s-%s' % (bname, egress_chain[:11])
        for router_info_inst in apply_list:
            v4filter_inst = router_info_inst.iptables_manager.ipv4['filter']
            calls = [mock.call.remove_chain('iv4fake-fw-uuid'),
                     mock.call.remove_chain('ov4fake-fw-uuid'),
                     mock.call.remove_chain('fwaas-default-policy'),
                     mock.call.add_chain('fwaas-default-policy'),
                     mock.call.add_rule('fwaas-default-policy', '-j DROP'),
                     mock.call.add_chain(ingress_chain),
                     mock.call.add_rule(ingress_chain, invalid_rule),
                     mock.call.add_rule(ingress_chain, est_rule),
                     mock.call.add_chain(egress_chain),
                     mock.call.add_rule(egress_chain, invalid_rule),
                     mock.call.add_rule(egress_chain, est_rule),
                     mock.call.add_rule(ingress_chain, rule1),
                     mock.call.add_rule(egress_chain, rule1),
                     mock.call.add_rule(ingress_chain, rule2),
                     mock.call.add_rule(egress_chain, rule2),
                     mock.call.add_rule(ingress_chain, rule3),
                     mock.call.add_rule(egress_chain, rule3),
                     mock.call.add_rule('FORWARD',
                                        '-o %s -j %s' % (if_prefix,
                                        ipt_mgr_ichain)),
                     mock.call.add_rule('FORWARD',
                                        '-i %s -j %s' % (if_prefix,
                                        ipt_mgr_echain)),
                     mock.call.add_rule('FORWARD',
                                        '-o %s -j %s-fwaas-defau' % (if_prefix,
                                        bname)),
                     mock.call.add_rule('FORWARD',
                                        '-i %s -j %s-fwaas-defau' % (if_prefix,
                                        bname))]
            v4filter_inst.assert_has_calls(calls)

    def test_create_firewall_no_rules(self):
        apply_list = self._fake_apply_list()
        firewall = self._fake_firewall_no_rule()
        self.firewall.create_firewall('legacy', apply_list, firewall)
        invalid_rule = '-m state --state INVALID -j DROP'
        est_rule = '-m state --state RELATED,ESTABLISHED -j ACCEPT'
        bname = fwaas.iptables_manager.binary_name
        for ip_version in (4, 6):
            ingress_chain = ('iv%s%s' % (ip_version, firewall['id']))
            egress_chain = ('ov%s%s' % (ip_version, firewall['id']))
            calls = [mock.call.remove_chain(
                     'iv%sfake-fw-uuid' % ip_version),
                     mock.call.remove_chain(
                         'ov%sfake-fw-uuid' % ip_version),
                     mock.call.remove_chain('fwaas-default-policy'),
                     mock.call.add_chain('fwaas-default-policy'),
                     mock.call.add_rule('fwaas-default-policy', '-j DROP'),
                     mock.call.add_chain(ingress_chain),
                     mock.call.add_rule(ingress_chain, invalid_rule),
                     mock.call.add_rule(ingress_chain, est_rule),
                     mock.call.add_chain(egress_chain),
                     mock.call.add_rule(egress_chain, invalid_rule),
                     mock.call.add_rule(egress_chain, est_rule),
                     mock.call.add_rule('FORWARD',
                                        '-o qr-+ -j %s-fwaas-defau' % bname),
                     mock.call.add_rule('FORWARD',
                                        '-i qr-+ -j %s-fwaas-defau' % bname)]
            if ip_version == 4:
                v4filter_inst = apply_list[0].iptables_manager.ipv4['filter']
                v4filter_inst.assert_has_calls(calls)
            else:
                v6filter_inst = apply_list[0].iptables_manager.ipv6['filter']
                v6filter_inst.assert_has_calls(calls)

    def test_create_firewall_with_rules(self):
        self._setup_firewall_with_rules(self.firewall.create_firewall)

    def test_create_firewall_with_rules_without_distributed_attr(self):
        self._setup_firewall_with_rules(self.firewall.create_firewall,
                                        distributed=None)

    def test_create_firewall_with_rules_two_routers(self):
        self._setup_firewall_with_rules(self.firewall.create_firewall,
                                        router_count=2)

    def test_update_firewall_with_rules(self):
        self._setup_firewall_with_rules(self.firewall.update_firewall)

    def test_update_firewall_with_rules_without_distributed_attr(self):
        self._setup_firewall_with_rules(self.firewall.update_firewall,
                                        distributed=None)

    def _test_delete_firewall(self, distributed=False):
        apply_list = self._fake_apply_list(distributed=distributed)
        firewall = self._fake_firewall_no_rule()
        self.firewall.delete_firewall('legacy', apply_list, firewall)
        ingress_chain = 'iv4%s' % firewall['id']
        egress_chain = 'ov4%s' % firewall['id']
        calls = [mock.call.remove_chain(ingress_chain),
                 mock.call.remove_chain(egress_chain),
                 mock.call.remove_chain('fwaas-default-policy')]
        apply_list[0].iptables_manager.ipv4['filter'].assert_has_calls(calls)

    def test_delete_firewall(self):
        self._test_delete_firewall()

    def test_delete_firewall_without_distributed_attr(self):
        self._test_delete_firewall(distributed=None)

    def test_create_firewall_with_admin_down(self):
        apply_list = self._fake_apply_list()
        rule_list = self._fake_rules_v4(FAKE_FW_ID, apply_list)
        firewall = self._fake_firewall_with_admin_down(rule_list)
        self.firewall.create_firewall('legacy', apply_list, firewall)
        calls = [mock.call.remove_chain('iv4fake-fw-uuid'),
                 mock.call.remove_chain('ov4fake-fw-uuid'),
                 mock.call.remove_chain('fwaas-default-policy'),
                 mock.call.add_chain('fwaas-default-policy'),
                 mock.call.add_rule('fwaas-default-policy', '-j DROP')]
        apply_list[0].iptables_manager.ipv4['filter'].assert_has_calls(calls)

    def test_create_firewall_with_rules_dvr_snat(self):
        self._setup_firewall_with_rules(self.firewall.create_firewall,
            distributed=True, distributed_mode='dvr_snat')

    def test_update_firewall_with_rules_dvr_snat(self):
        self._setup_firewall_with_rules(self.firewall.update_firewall,
            distributed=True, distributed_mode='dvr_snat')

    def test_create_firewall_with_rules_dvr(self):
        self._setup_firewall_with_rules(self.firewall.create_firewall,
            distributed=True, distributed_mode='dvr')

    def test_update_firewall_with_rules_dvr(self):
        self._setup_firewall_with_rules(self.firewall.update_firewall,
            distributed=True, distributed_mode='dvr')

    def test_remove_conntrack_new_firewall(self):
        apply_list = self._fake_apply_list()
        firewall = self._fake_firewall_no_rule()
        self.firewall.create_firewall(FW_LEGACY, apply_list, firewall)
        for router_info_inst in apply_list:
            namespace = router_info_inst.iptables_manager.namespace
            calls = [mock.call(namespace)]
            self.conntrack_driver.flush_entries.assert_has_calls(calls)

    def test_remove_conntrack_inserted_rule(self):
        apply_list = self._fake_apply_list()
        rule_list = self._fake_rules_v4(FAKE_FW_ID, apply_list)
        firewall = self._fake_firewall(rule_list)
        self.firewall.create_firewall(FW_LEGACY, apply_list, firewall)
        self.firewall.pre_firewall = dict(firewall)
        insert_rule = {'enabled': True,
                 'action': 'deny',
                 'ip_version': 4,
                 'protocol': 'icmp',
                 'id': 'fake-fw-rule'}
        rule_list.insert(2, insert_rule)
        firewall = self._fake_firewall(rule_list)
        self.firewall.update_firewall(FW_LEGACY, apply_list, firewall)
        rules_changed = [
            {'destination_port': '23',
             'position': '2',
             'protocol': 'tcp',
             'ip_version': 4,
             'enabled': True,
             'action': 'reject',
             'id': 'fake-fw-rule3'},
            {'destination_port': '23',
             'position': '3',
             'protocol': 'tcp',
             'ip_version': 4,
             'enabled': True,
             'action': 'reject',
             'id': 'fake-fw-rule3'}
        ]
        rules_inserted = [
            {'id': 'fake-fw-rule',
             'protocol': 'icmp',
             'ip_version': 4,
             'enabled': True,
             'action': 'deny',
             'position': '2'}
        ]
        for router_info_inst in apply_list:
            namespace = router_info_inst.iptables_manager.namespace
            self.conntrack_driver.delete_entries.assert_called_once_with(
                rules_changed + rules_inserted, namespace
            )

    def test_remove_conntrack_removed_rule(self):
        apply_list = self._fake_apply_list()
        rule_list = self._fake_rules_v4(FAKE_FW_ID, apply_list)
        firewall = self._fake_firewall(rule_list)
        self.firewall.create_firewall(FW_LEGACY, apply_list, firewall)
        self.firewall.pre_firewall = dict(firewall)
        remove_rule = rule_list[1]
        rule_list.remove(remove_rule)
        firewall = self._fake_firewall(rule_list)
        self.firewall.update_firewall(FW_LEGACY, apply_list, firewall)
        rules_changed = [
            {'destination_port': '23',
             'position': '2',
             'protocol': 'tcp',
             'ip_version': 4,
             'enabled': True,
             'action': 'reject',
             'id': 'fake-fw-rule3'},
            {'destination_port': '23',
             'position': '1',
             'protocol': 'tcp',
             'ip_version': 4,
             'enabled': True,
             'action': 'reject',
             'id': 'fake-fw-rule3'}
        ]
        rules_removed = [
            {'enabled': True,
             'position': '1',
             'protocol': 'tcp',
             'id': 'fake-fw-rule2',
             'ip_version': 4,
             'action': 'deny',
             'destination_port': '22'}
        ]
        for router_info_inst in apply_list:
            namespace = router_info_inst.iptables_manager.namespace
            self.conntrack_driver.delete_entries.assert_called_once_with(
                rules_changed + rules_removed, namespace
            )

    def test_remove_conntrack_changed_rule(self):
        apply_list = self._fake_apply_list()
        rule_list = self._fake_rules_v4(FAKE_FW_ID, apply_list)
        firewall = self._fake_firewall(rule_list)
        self.firewall.create_firewall(FW_LEGACY, apply_list, firewall)
        income_rule = {'enabled': True,
                 'action': 'deny',
                 'ip_version': 4,
                 'protocol': 'tcp',
                 'id': 'fake-fw-rule3'}
        rule_list[2] = income_rule
        firewall = self._fake_firewall(rule_list)
        self.firewall.update_firewall(FW_LEGACY, apply_list, firewall)
        rules_changed = [
            {'id': 'fake-fw-rule3',
             'enabled': True,
             'action': 'reject',
             'position': '2',
             'destination_port': '23',
             'ip_version': 4,
             'protocol': 'tcp'},
            {'position': '2',
             'enabled': True,
             'action': 'deny',
             'id': 'fake-fw-rule3',
             'ip_version': 4,
             'protocol': 'tcp'}
        ]
        for router_info_inst in apply_list:
            namespace = router_info_inst.iptables_manager.namespace
            self.conntrack_driver.delete_entries.assert_called_once_with(
                rules_changed, namespace
            )
