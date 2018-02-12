# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

from amaasutils.logging_utils import DEFAULT_LOGGING
import random
import requests_mock
import unittest

from amaascore.assets.asset import Asset
from amaascore.assets.bond_option import BondOption
from amaascore.assets.foreign_exchange import ForeignExchange
from amaascore.assets.interface import AssetsInterface
from amaascore.tools.generate_asset import generate_asset, generate_foreignexchange, generate_assets
from tests.unit.config import STAGE

import logging.config
logging.config.dictConfig(DEFAULT_LOGGING)


class AssetsInterfaceTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.assets_interface = AssetsInterface(environment=STAGE)

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.asset_manager_id = random.randint(1, 2**31-1)
        self.asset = generate_asset(asset_manager_id=self.asset_manager_id)
        self.asset_id = self.asset.asset_id

    def tearDown(self):
        pass

    def test_New(self):
        self.assertIsNone(self.asset.created_time)
        asset = self.assets_interface.new(self.asset)
        # TODO - this should be populated by the New call.
        #self.assertIsNotNone(asset.created_time)
        self.assertEqual(asset.asset_id, self.asset_id)

    def test_CreateMany(self):
        assets = [generate_asset(asset_manager_id=self.asset_manager_id) for _ in range(random.randint(1,5))]
        results = self.assets_interface.create_many(assets)
        self.assertEqual(len(assets), len(results))

    def test_Amend(self):
        asset = self.assets_interface.new(self.asset)
        self.assertEqual(asset.version, 1)
        asset.description = 'TEST'
        asset = self.assets_interface.amend(asset)
        self.assertEqual(asset.description, 'TEST')
        self.assertEqual(asset.version, 2)

    def test_Upsert_Amend(self):
        asset = self.assets_interface.new(self.asset)
        self.assertEqual(asset.version, 1)
        asset.description = 'TEST'
        asset = self.assets_interface.upsert(asset)
        self.assertEqual(asset.description, 'TEST')
        self.assertEqual(asset.version, 2)

    def test_Upsert_New(self):
        asset = self.assets_interface.upsert(self.asset)
        self.assertEqual(asset.version, 1)
        self.assertEqual(asset.asset_id, self.asset.asset_id)

    def test_Partial(self):
        self.assets_interface.new(self.asset)
        description = 'XXX'
        updates = {'description': description}
        asset = self.assets_interface.partial(asset_manager_id=self.asset_manager_id,
                                              asset_id=self.asset_id, updates=updates)
        self.assertEqual(asset.version, 2)
        self.assertEqual(asset.description, description)

    def test_Retrieve(self):
        self.assets_interface.new(self.asset)
        fx = generate_foreignexchange()
        fx = self.assets_interface.new(fx)
        asset = self.assets_interface.retrieve(self.asset.asset_manager_id, self.asset.asset_id)
        fx = self.assets_interface.retrieve(fx.asset_manager_id, fx.asset_id)
        self.assertEqual(type(asset), Asset)
        self.assertEqual(type(fx), ForeignExchange)

    def test_Deactivate(self):
        self.assets_interface.new(self.asset)
        self.assets_interface.deactivate(self.asset.asset_manager_id, self.asset.asset_id)
        asset = self.assets_interface.retrieve(self.asset.asset_manager_id, self.asset.asset_id)
        self.assertEqual(asset.asset_id, self.asset_id)
        self.assertEqual(asset.asset_status, 'Inactive')

    @requests_mock.Mocker()
    def test_Search(self, mocker):
        # This test is somewhat fake - but the integration tests are for the bigger picture
        endpoint = '%s/assets/%s' % (self.assets_interface.endpoint, self.asset_manager_id)
        assets = generate_assets(asset_manager_ids=[self.asset_manager_id])
        mocker.get(endpoint, json=[asset.to_json() for asset in assets])
        all_assets = self.assets_interface.search(self.asset_manager_id)
        self.assertEqual(assets, all_assets)

    @requests_mock.Mocker()
    def test_AssetsByAssetManager(self, mocker):
        # This test is somewhat fake - but the integration tests are for the bigger picture
        endpoint = '%s/assets/%s' % (self.assets_interface.endpoint, self.asset_manager_id)
        assets = generate_assets(asset_manager_ids=[self.asset_manager_id])
        mocker.get(endpoint, json=[asset.to_json() for asset in assets])
        asset_manager_assets = self.assets_interface.assets_by_asset_manager(asset_manager_id=self.asset_manager_id)
        self.assertEqual(assets, asset_manager_assets)

    def test_ChildrenPopulated(self):
        asset = self.assets_interface.new(self.asset)
        retrieved_asset = self.assets_interface.retrieve(asset_manager_id=self.asset_manager_id,
                                                         asset_id=self.asset_id)
        self.assertGreater(len(asset.references), 0)
        self.assertEqual(asset.references, retrieved_asset.references)

    def test_Unicode(self):
        unicode_description = '日本語入力'
        self.asset.description = unicode_description
        asset = self.assets_interface.new(self.asset)
        self.assertEqual(asset.description, unicode_description)

    def test_Clear(self):
        self.assets_interface.new(self.asset)
        count = self.assets_interface.clear(self.asset_manager_id)
        self.assertEqual(count, 1)
        results = self.assets_interface.search(asset_manager_id=self.asset_manager_id)
        # Strip out the 'shared' assets
        results = [result for result in results if result.asset_manager_id == self.asset_manager_id]
        self.assertEqual(len(results), 0)

if __name__ == '__main__':
    unittest.main()
