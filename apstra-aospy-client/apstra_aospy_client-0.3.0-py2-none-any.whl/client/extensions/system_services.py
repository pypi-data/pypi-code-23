# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/eula

import six
import retrying

from ..group import Group, GroupItem


class SystemServiceItem(GroupItem):
    DEFAULT_INTERVAL = 30

    def get_data(self):
        """ returns the current collector data items """
        got = self.api.get(self.url + "/data")
        if not got.ok:
            raise RuntimeError("unable to retrieve service data", self, got)
        return got.json()['items']

    def read(self):
        """ override the read method to return the current collector data """
        return self.get_data()

    def get_status(self):
        """
        Used to return the status of this collector.

        Notes
        -----
        This is only valid for "custom" services, not built-in services.
        # TODO: remove this note when AOS converges on collector types
        """
        @retrying.retry(wait_fixed=1000, stop_max_delay=5000)
        def get_status():
            self.group.fetch_items()
            me = self.group[self.label]
            assert me.value['status']
            return me.value

        self.obj = get_status()
        return self

    def start(self, interval=None, config=None):
        """ use this method to start a service """

        body = {
            'name': self.label,
            'interval': interval or self.DEFAULT_INTERVAL,
            'input': config or ''}

        got = self.api.post(self.group.url, json=body)
        if not got.ok:
            raise RuntimeError("unable to create system service",
                               self, got)

        return self.get_status()


class SystemServicesGroup(Group):
    group_endpoint = '/services'
    group_items = 'services'
    groupitem_id = 'name'
    groupitem_label = 'name'
    groupitem_class = SystemServiceItem

    def fetch_items_hook(self, catalog_data):
        """
        override default because the AOS API returns non-standard structure
            { 'services': { service_name: <dict> }}
        """
        return (item for item in six.itervalues(catalog_data[self.group_items]))


def plugin(system):
    return SystemServicesGroup(system)
