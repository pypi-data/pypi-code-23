# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/eula

from ..group import Group, GroupItem
from ..extensible import Extensible


class SystemItem(GroupItem, Extensible):
    extension_groups = ['aospy.client.systems']

    # -------------------------------------------------------------------------
    #                               PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def facts(self):
        return self.value.get('facts')

    @property
    def mgmt_ipaddr(self):
        return self.facts['mgmt_ipaddr']

    @property
    def vendor(self):
        return self.facts['vendor']

    @property
    def serial_number(self):
        return self.facts['serial_number']

    @property
    def hcl_model(self):
        return self.facts['aos_hcl_model']

    @property
    def status(self):
        try:
            return self.value["status"]['state']
        except KeyError:
            return None

    @property
    def hostname(self):
        try:
            return self.value["status"]['hostname']
        except KeyError:
            return None

    @property
    def user_config(self):
        self.read()
        return self.value.get('user_config')

    @user_config.setter
    def user_config(self, value):
        got = self.api.put(self.url, json=dict(user_config=value))
        if not got.ok:
            raise RuntimeError('unable to set user_config', self, got)

    # -------------------------------------------------------------------------
    #                        PUBLIC METHODS
    # -------------------------------------------------------------------------

    def decommission(self):
        config = self.user_config or {}
        config['admin_state'] = 'decomm'
        config['aos_hcl_model'] = self.hcl_model
        self.user_config = config

    def acknowledge(self):
        config = self.user_config or {}
        config['admin_state'] = 'normal'
        config['aos_hcl_model'] = self.hcl_model
        self.user_config = config

    def get_anomalies(self):
        got = self.api.get(self.url + "/anomalies")
        if not got.ok:
            raise RuntimeError("Unable to get system anomalies", self, got)

        return got.json()

    def get_configuration(self):
        got = self.api.get(self.url + "/configuration")
        if not got.ok:
            raise RuntimeError("Unable to get system configuration", self, got)

        return got.json()

    def get_interface_counters(self):
        got = self.api.get(self.url + "/counters")
        if not got.ok:
            raise RuntimeError("Unable to get system interface counters", self, got)

        return got.json()['items']


class SystemsGroup(Group):
    group_endpoint = '/api/systems'
    groupitem_id = 'device_key'
    groupitem_label = 'facts.mgmt_ipaddr'
    groupitem_class = SystemItem


def plugin(aos):
    return SystemsGroup(aos)
