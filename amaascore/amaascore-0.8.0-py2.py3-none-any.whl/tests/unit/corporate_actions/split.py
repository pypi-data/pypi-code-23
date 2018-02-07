from __future__ import absolute_import, division, print_function, unicode_literals

from decimal import Decimal
import unittest

from amaascore.corporate_actions.split import Split
from amaascore.tools.generate_corporate_action import generate_split


class SplitTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.split = generate_split()
        self.corporate_action_id = self.split.corporate_action_id

    def tearDown(self):
        pass

    def test_Split(self):
        self.assertEqual(type(self.split), Split)

if __name__ == '__main__':
    unittest.main()
