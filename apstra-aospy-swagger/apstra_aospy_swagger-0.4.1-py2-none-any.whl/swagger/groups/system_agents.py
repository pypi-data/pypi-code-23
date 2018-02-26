# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/eula

from aospy.swagger.indexer import Indexer, IndexItem

__all__ = ['SystemAgents']


class SystemAgentItem(IndexItem):

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
        state = self.value['status']['connection_state']
        return bool(state.lower() == 'connected')


class SystemAgents(Indexer):
    def __init__(self, aos):

        super(SystemAgents, self).__init__(
            rqst=aos.request.system_agents.get_api_system_agents,
            name_from='id',
            index_item_type=SystemAgentItem)

        self.run()
