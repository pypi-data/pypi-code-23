# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

from amaasutils.logging_utils import DEFAULT_LOGGING
import random
import requests_mock
import unittest

from amaascore.parties.broker import Broker
from amaascore.parties.party import Party
from amaascore.parties.interface import PartiesInterface
from amaascore.tools.generate_party import generate_party, generate_broker, generate_parties
from tests.unit.config import STAGE

import logging.config
logging.config.dictConfig(DEFAULT_LOGGING)


class PartiesInterfaceTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.parties_interface = PartiesInterface(environment=STAGE)

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.asset_manager_id = random.randint(1, 2**31-1)
        self.party = generate_party(asset_manager_id=self.asset_manager_id)
        self.party_id = self.party.party_id

    def tearDown(self):
        pass

    def test_New(self):
        self.assertIsNone(self.party.created_time)
        party = self.parties_interface.new(self.party)
        # TODO - this should be populated by the New call.
        #self.assertIsNotNone(party.created_time)
        self.assertEqual(party.display_name, self.party.display_name)
        self.assertEqual(party.party_id, self.party_id)

    def test_Amend(self):
        party = self.parties_interface.new(self.party)
        self.assertEqual(party.version, 1)
        party.description = 'TEST'
        party = self.parties_interface.amend(party)
        self.assertEqual(party.description, 'TEST')
        self.assertEqual(party.version, 2)

    def test_Partial(self):
        self.parties_interface.new(self.party)
        base_currency = 'XXX'
        updates = {'base_currency': base_currency}
        party = self.parties_interface.partial(asset_manager_id=self.asset_manager_id,
                                               party_id=self.party_id, updates=updates)
        self.assertEqual(party.version, 2)
        self.assertEqual(party.base_currency, base_currency)

    def test_Retrieve(self):
        self.parties_interface.new(self.party)
        broker = generate_broker()
        broker = self.parties_interface.new(broker)
        party = self.parties_interface.retrieve(self.party.asset_manager_id, self.party.party_id)
        broker = self.parties_interface.retrieve(broker.asset_manager_id, broker.party_id)
        self.assertEqual(type(party), Party)
        self.assertEqual(type(broker), Broker)

    def test_Deactivate(self):
        self.parties_interface.new(self.party)
        self.parties_interface.deactivate(self.party.asset_manager_id, self.party.party_id)
        party = self.parties_interface.retrieve(self.party.asset_manager_id, self.party.party_id)
        self.assertEqual(party.party_id, self.party_id)
        self.assertEqual(party.party_status, 'Inactive')

    @requests_mock.Mocker()
    def test_Search(self, mocker):
        # This test is somewhat fake - but the integration tests are for the bigger picture
        endpoint = '%s/parties' % self.parties_interface.endpoint
        parties = generate_parties(asset_manager_ids=[self.asset_manager_id, self.asset_manager_id+1])
        mocker.get(endpoint, json=[party.to_json() for party in parties])
        all_parties = self.parties_interface.search(self.asset_manager_id)
        self.assertEqual(parties, all_parties)

    @requests_mock.Mocker()
    def test_PartiesByAssetManager(self, mocker):
        # This test is somewhat fake - but the integration tests are for the bigger picture
        endpoint = '%s/parties/%s' % (self.parties_interface.endpoint, self.asset_manager_id)
        parties = generate_parties(asset_manager_ids=[self.asset_manager_id])
        mocker.get(endpoint, json=[party.to_json() for party in parties])
        asset_manager_parties = self.parties_interface.parties_by_asset_manager(asset_manager_id=self.asset_manager_id)
        self.assertEqual(parties, asset_manager_parties)

    def test_ChildrenPopulated(self):
        party = self.parties_interface.new(self.party)
        retrieved_party = self.parties_interface.retrieve(asset_manager_id=self.asset_manager_id,
                                                          party_id=self.party_id)
        self.assertGreater(len(party.addresses), 0)
        self.assertGreater(len(party.emails), 0)
        self.assertGreater(len(party.references), 0)
        self.assertEqual(party.addresses, retrieved_party.addresses)
        self.assertEqual(party.emails, retrieved_party.emails)
        self.assertEqual(party.references, retrieved_party.references)

    def test_Unicode(self):
        unicode_description = '日本語入力'
        self.party.description = unicode_description
        party = self.parties_interface.new(self.party)
        self.assertEqual(party.description, unicode_description)

    def test_Clear(self):
        self.parties_interface.new(self.party)
        count = self.parties_interface.clear(self.asset_manager_id)
        self.assertEqual(count, 1)
        results = self.parties_interface.search(asset_manager_id=self.asset_manager_id)
        # Strip out the 'shared' parties
        results = [result for result in results if result.asset_manager_id == self.asset_manager_id]
        self.assertEqual(len(results), 0)

if __name__ == '__main__':
    unittest.main()
