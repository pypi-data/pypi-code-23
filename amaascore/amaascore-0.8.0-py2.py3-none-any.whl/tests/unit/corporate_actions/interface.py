# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

from amaasutils.logging_utils import DEFAULT_LOGGING
import random
import requests_mock
import unittest

from amaascore.corporate_actions.interface import CorporateActionsInterface
from amaascore.tools.generate_corporate_action import generate_corporate_action, generate_corporate_actions
from tests.unit.config import STAGE

import logging.config
logging.config.dictConfig(DEFAULT_LOGGING)


class CorporateActionsInterfaceTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.corporate_actions_interface = CorporateActionsInterface(environment=STAGE)

    def setUp(self):
        self.maxDiff = None
        self.longMessage = True  # Print complete error message on failure
        self.asset_manager_id = random.randint(1, 2**31-1)
        self.corporate_action = generate_corporate_action(asset_manager_id=self.asset_manager_id)
        self.corporate_action_id = self.corporate_action.corporate_action_id

    def tearDown(self):
        pass

    def test_New(self):
        self.assertIsNone(self.corporate_action.created_time)
        corporate_action = self.corporate_actions_interface.new(self.corporate_action)
        # TODO - this should be populated by the New call.
        #self.assertIsNotNone(corporate_action.created_time)
        self.assertEqual(corporate_action.corporate_action_id, self.corporate_action_id)

    def test_Amend(self):
        corporate_action = self.corporate_actions_interface.new(self.corporate_action)
        self.assertEqual(corporate_action.version, 1)
        corporate_action.asset_id = 'TEST'
        corporate_action = self.corporate_actions_interface.amend(corporate_action)
        self.assertEqual(corporate_action.asset_id, 'TEST')
        self.assertEqual(corporate_action.version, 2)

    def test_Retrieve(self):
        self.corporate_actions_interface.new(self.corporate_action)
        corporate_action = self.corporate_actions_interface.retrieve(self.corporate_action.asset_manager_id,
                                                                     self.corporate_action.corporate_action_id)
        self.assertEqual(corporate_action.corporate_action_id, self.corporate_action_id)

    def test_Cancel(self):
        self.corporate_actions_interface.new(self.corporate_action)
        self.corporate_actions_interface.cancel(self.corporate_action.asset_manager_id,
                                                self.corporate_action.corporate_action_id)
        corporate_action = self.corporate_actions_interface.retrieve(self.corporate_action.asset_manager_id,
                                                                     self.corporate_action.corporate_action_id)
        self.assertEqual(corporate_action.corporate_action_id, self.corporate_action_id)
        self.assertEqual(corporate_action.corporate_action_status, 'Cancelled')

    @requests_mock.Mocker()
    def test_Search(self, mocker):
        # This test is somewhat fake - but the integration tests are for the bigger picture
        endpoint = '%s/corporate-actions' % self.corporate_actions_interface.endpoint
        corporate_actions = generate_corporate_actions(asset_manager_ids=[self.asset_manager_id])
        mocker.get(endpoint, json=[corporate_action.to_json() for corporate_action in corporate_actions])
        all_corporate_actions = self.corporate_actions_interface.search(self.asset_manager_id)
        self.assertEqual(corporate_actions, all_corporate_actions)

    @requests_mock.Mocker()
    def test_CorporateActionsByAssetManager(self, mocker):
        # This test is somewhat fake - but the integration tests are for the bigger picture
        endpoint = '%s/corporate-actions/%s' % (self.corporate_actions_interface.endpoint, self.asset_manager_id)
        corporate_actions = generate_corporate_actions(asset_manager_ids=[self.asset_manager_id])
        mocker.get(endpoint, json=[corporate_action.to_json() for corporate_action in corporate_actions])
        amca = self.corporate_actions_interface.corporate_actions_by_asset_manager(self.asset_manager_id)
        self.assertEqual(corporate_actions, amca)

    def test_Unicode(self):
        unicode_description = '日本語入力'
        self.corporate_action.description = unicode_description
        corporate_action = self.corporate_actions_interface.new(self.corporate_action)
        self.assertEqual(corporate_action.description, unicode_description)

    def test_Clear(self):
        self.corporate_actions_interface.new(self.corporate_action)
        count = self.corporate_actions_interface.clear(self.asset_manager_id)
        self.assertEqual(count, 1)
        results = self.corporate_actions_interface.search(asset_manager_id=self.asset_manager_id)
        # Strip out the 'shared' corporate actions
        results = [result for result in results if result.asset_manager_id == self.asset_manager_id]
        self.assertEqual(len(results), 0)

if __name__ == '__main__':
    unittest.main()
