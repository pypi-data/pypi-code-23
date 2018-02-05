# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/eula

from ..group import Group, GroupItem


class SystemAgentItem(GroupItem):

    @property
    def serial_number(self):
        try:
            return self.value['status']['system_id']
        except KeyError:
            return None

    @property
    def mgmt_ipaddr(self):
        try:
            return self.value['config']['management_ip']
        except KeyError:
            return None

    @property
    def is_connected(self):
        state = self['status']['connection_state']
        return bool(state.lower() == 'connected')


class SystemAgents(Group):
    group_endpoint = '/api/system-agents'
    groupitem_label = 'id'
    groupitem_class = SystemAgentItem


def plugin(aos):
    return SystemAgents(aos)
