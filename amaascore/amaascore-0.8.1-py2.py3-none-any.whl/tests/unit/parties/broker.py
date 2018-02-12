from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from amaascore.parties.broker import Broker
from amaascore.parties.company import Company
from amaascore.tools.generate_party import generate_broker


class BrokerTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.company = generate_broker()  # Using a broker as an example company
        self.party_id = self.company.party_id

    def tearDown(self):
        pass

    def test_Broker(self):
        self.assertEqual(type(self.company), Broker)
        self.assertTrue(isinstance(self.company, Company))

if __name__ == '__main__':
    unittest.main()
