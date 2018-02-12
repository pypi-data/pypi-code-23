from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from amaascore.transactions.position import Position
from amaascore.tools.generate_transaction import generate_position


class PositionTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.position = generate_position()

    def tearDown(self):
        pass

    def test_Transaction(self):
        self.assertEqual(type(self.position), Position)

if __name__ == '__main__':
    unittest.main()
