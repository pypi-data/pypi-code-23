# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

from amaasutils.logging_utils import DEFAULT_LOGGING
import random
import requests_mock
import unittest

from amaascore.monitor.interface import MonitorInterface
from amaascore.tools.generate_monitor_item import generate_item, generate_items
from tests.unit.config import STAGE

import logging.config
logging.config.dictConfig(DEFAULT_LOGGING)


class MonitorInterfaceTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.monitor_interface = MonitorInterface(environment=STAGE)

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.maxDiff = None
        self.asset_manager_id = random.randint(1, 2**31-1)
        self.item = generate_item(asset_manager_id=self.asset_manager_id)
        self.item_id = self.item.item_id

    def tearDown(self):
        pass

    def test_New(self):
        self.assertIsNone(self.item.created_time)
        item = self.monitor_interface.new_item(self.item)
        # TODO - this should be populated by the New call.
        #self.assertIsNotNone(item.created_time)
        self.assertEqual(item.item_id, self.item_id)

    def test_Retrieve(self):
        self.monitor_interface.new_item(self.item)
        item = self.monitor_interface.retrieve_item(self.item.asset_manager_id, self.item.item_id)
        self.assertEqual(item.item_id, self.item_id)

    def test_Resubmit(self):
        self.monitor_interface.new_item(self.item)
        item = self.monitor_interface.resubmit_item(self.item.asset_manager_id, self.item.item_id)
        self.assertEqual(item.item_id, self.item_id)
        self.assertEqual(item.item_status, 'Resubmitted')
        self.assertEqual(item.version, 2)

    def test_Close(self):
        self.monitor_interface.new_item(self.item)
        self.monitor_interface.close_item(self.item.asset_manager_id, self.item.item_id)
        item = self.monitor_interface.retrieve_item(self.item.asset_manager_id, self.item.item_id)
        self.assertEqual(item.item_id, self.item_id)
        self.assertEqual(item.item_status, 'Closed')

    @requests_mock.Mocker()
    def test_Search(self, mocker):
        # This test is somewhat fake - but the integration tests are for the bigger picture
        endpoint = '%s/items' % self.monitor_interface.endpoint
        items = generate_items(asset_manager_ids=[self.asset_manager_id])
        mocker.get(endpoint, json=[item.to_json() for item in items])
        all_items = self.monitor_interface.search_items(self.asset_manager_id)
        self.assertEqual(items, all_items)

    @requests_mock.Mocker()
    def test_ItemsByAssetManager(self, mocker):
        # This test is somewhat fake - but the integration tests are for the bigger picture
        endpoint = '%s/items/%s' % (self.monitor_interface.endpoint, self.asset_manager_id)
        items = generate_items(asset_manager_ids=[self.asset_manager_id])
        mocker.get(endpoint, json=[item.to_json() for item in items])
        asset_manager_items = self.monitor_interface.items_by_asset_manager(asset_manager_id=self.asset_manager_id)
        self.assertEqual(items, asset_manager_items)

    def test_Unicode(self):
        unicode_message = '日本語入力'
        self.item.message = unicode_message
        item = self.monitor_interface.new_item(self.item)
        self.assertEqual(item.message, unicode_message)

    def test_Clear(self):
        self.monitor_interface.new_item(self.item)
        count = self.monitor_interface.clear(self.asset_manager_id)
        self.assertEqual(count, 1)
        results = self.monitor_interface.search_items(asset_manager_id=self.asset_manager_id)
        self.assertEqual(len(results), 0)

if __name__ == '__main__':
    unittest.main()
