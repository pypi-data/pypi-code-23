# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/eula

# import six
# import retrying
from cached_property import cached_property
from aospy.swagger.indexer import Indexer, IndexItem


class SystemServiceItem(IndexItem):
    DEFAULT_INTERVAL = 30

    @cached_property
    def url(self):
        base_url = super(SystemServiceItem, self).url
        return base_url.format(**self.index.run_kwargs)

    def get_data(self):
        """ returns the current collector data items """
        got = self.api.get(self.url + "/data")
        if not got.ok:
            raise RuntimeError("unable to retrieve service data", self, got)

        return got.json()['items']

    def read(self):
        """ override the read method to return the current collector data """
        return self.get_data()

    # def get_status(self):
    #     """
    #     Used to return the status of this collector.
    #
    #     Notes
    #     -----
    #     This is only valid for "custom" services, not built-in services.
    #     # TODO: remove this note when AOS converges on collector types
    #     """
    #     @retrying.retry(wait_fixed=1000, stop_max_delay=5000)
    #     def get_status():
    #         self.group.fetch_items()
    #         me = self.group[self.label]
    #         assert me.value['status']
    #         return me.value
    #
    #     self.obj = get_status()
    #     return self

    # def start(self, interval=None, config=None):
    #     """ use this method to start a service """
    #
    #     body = {
    #         'name': self.name,
    #         'interval': interval or self.DEFAULT_INTERVAL,
    #         'input': config or ''}
    #
    #     got = self.api.post(self.group.url, json=body)
    #     if not got.ok:
    #         raise RuntimeError("unable to create system service",
    #                            self, got)
    #
    #     return self.get_status()


class SystemServices(Indexer):

    def __init__(self, aos, system):
        rqst = aos.request.systems.get_api_systems_system_id_services

        super(SystemServices, self).__init__(
            rqst=rqst, index_item_type=SystemServiceItem)

        self.run(system_id=system.id)
