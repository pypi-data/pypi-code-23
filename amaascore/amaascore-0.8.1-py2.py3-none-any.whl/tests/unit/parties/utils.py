from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from amaascore.parties.utils import json_to_party
from amaascore.tools.generate_party import generate_party


class PartyUtilsTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure

    def tearDown(self):
        pass

    def test_JsonToParty(self):
        party = generate_party()
        json_party = party.to_json()
        gen_party = json_to_party(json_party)
        self.assertEqual(gen_party, party)

if __name__ == '__main__':
    unittest.main()
