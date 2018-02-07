from __future__ import absolute_import, division, print_function, unicode_literals

from decimal import Decimal
import unittest

from amaascore.corporate_actions.corporate_action import CorporateAction
from amaascore.tools.generate_corporate_action import generate_corporate_action


class CorporateActionTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.generate_corporate_action = generate_corporate_action()
        self.corporate_action_id = self.generate_corporate_action.corporate_action_id

    def tearDown(self):
        pass

    def test_CorporateAction(self):
        self.assertEqual(type(self.generate_corporate_action), CorporateAction)

if __name__ == '__main__':
    unittest.main()
