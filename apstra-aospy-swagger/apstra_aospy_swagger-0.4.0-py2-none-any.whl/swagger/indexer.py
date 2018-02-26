# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula

from first import first
import halutz.indexer as hindexer

__all__ = ['Indexer', 'IndexItem']


class IndexItem(hindexer.IndexItem):
    def __init__(self, index, **kwargs):
        super(IndexItem, self).__init__(index=index, **kwargs)
        self.api = self.index.rqst.client.remote.api

    @property
    def url(self):
        rqst = self.index.rqst
        s_url = rqst.client.server_url
        r_path = rqst.path

        # the r_path starts with "/api"
        return "%s%s/%s" % (s_url, r_path, self.id)


class Indexer(hindexer.Indexer):
    name_from_anyof = ['label', 'display_name']
    id_from_anyof = ['id']

    def __init__(self, rqst,
                 name_from=None, id_from=None,
                 response_code=None,                # will use default if not provided
                 index_item_type=None):             # will use default if not provided

        super(Indexer, self).__init__(
            rqst, name_from=name_from, id_from=id_from,
            index_item_type=index_item_type or IndexItem,
            response_code=response_code)

        # try to set values from the "anyof" list items.

        if not name_from:
            self.name_from = first(prop for prop in self.items_properties
                                   if prop in self.name_from_anyof)

        if not id_from:
            self.id_from = first(prop for prop in self.items_properties
                                 if prop in self.id_from_anyof)

    # def create(self, value=None, replace=False, timeout=5000):
    #     # check to see if this item currently exists, using the name/URI
    #     # when this instances was instantiated from the collection; *not*
    #     # from the `value` data.
    #
    #     def throw_duplicate(name):
    #         raise ValueError(
    #             "'%s' already exists" % name, self)
    #
    #     if self.exists:
    #         if not replace:
    #             throw_duplicate(self.name)
    #
    #         try:
    #             self.delete()
    #         except RuntimeError as exc:
    #             resp = exc.args[2]
    #             if resp.status_code != 404:
    #                 raise
    #
    #     # the caller can either pass the new data to this method, or they
    #     # could have already assigned it into the :prop:`value`.  This
    #     # latter approach should be discouraged.
    #
    #     if value is not None:
    #         self.value = value
    #
    #     # now check to see if the new value/name exists.  if the value
    #     # does not include the label value, we need to auto-set it from
    #     # the instance name value.
    #
    #     new_name = self.group.get_item_label(self.value)
    #     if not new_name:
    #         new_name = self.label
    #         self.value[self.group.groupitem_label] = new_name
    #
    #     if new_name in self.group:
    #         throw_duplicate(new_name)
    #
    #     # at this point we should be good to execute the POST and
    #     # create the new item in the server
    #
    #     got = self.api.post(self.group.url, json=self.value)
    #     if not got.ok:
    #         raise RuntimeError('unable to create item', self, got)
    #
    #     body = got.json()
    #
    #     @retrying.retry(wait_fixed=1000, stop_max_delay=timeout)
    #     def await_item():
    #         self.group.fetch_items()
    #         assert new_name in self.group.labels
    #
    #     uid = body.get('id') or self.group.get_item_id(body)
    #     while not uid:
    #         await_item()
    #         body = self.group.catalog[new_name]
    #
    #     self.id = body.get('id') or self.group.get_item_id(body)
    #
    #     # now add this item to the parent collection so it can be used by other
    #     # invocations
    #
    #     self.group += self
    #     return self
