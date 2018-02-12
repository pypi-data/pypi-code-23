from __future__ import absolute_import, division, print_function, unicode_literals

from decimal import Decimal
import unittest

from amaascore.corporate_actions.dividend import Dividend
from amaascore.tools.generate_corporate_action import generate_dividend


class DividendTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.dividend = generate_dividend()
        self.corporate_action_id = self.dividend.corporate_action_id

    def tearDown(self):
        pass

    def test_Dividend(self):
        self.assertEqual(type(self.dividend), Dividend)

if __name__ == '__main__':
    unittest.main()
