#! /usr/bin/env python

from scrapy.exporters import BaseItemExporter

from twisted.internet import defer
from txmongo.connection import ConnectionPool


class MongoExporter(BaseItemExporter):

    def __init__(self, **kwarg):
        self._configure(kwarg, dont_fail=True)
        self.mongo_uri = kwarg.get("mongo_uri")
        self.client = kwarg.get("mongo_client")  # in most cases, will be None

        self._db = None
        self._collection = None

    def export_item(self, item):
        raise NotImplementedError

    @defer.inlineCallbacks
    def start_exporting(self):
        self.client = yield ConnectionPool(self.mongo_uri)

    def finish_exporting(self):
        self.client.disconnect()

