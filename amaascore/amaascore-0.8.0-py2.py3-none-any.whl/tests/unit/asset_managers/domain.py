from __future__ import absolute_import, division, print_function, unicode_literals

import unittest
from amaascore.asset_managers.domain import Domain
from amaascore.tools.generate_asset_manager import generate_domain


class DomainTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.domain = generate_domain()

    def tearDown(self):
        pass

    def test_Domain(self):
        self.assertEqual(type(self.domain), Domain)

if __name__ == '__main__':
    unittest.main()
