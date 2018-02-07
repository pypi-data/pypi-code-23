from __future__ import absolute_import, division, print_function, unicode_literals

import copy
import json
import unittest

from amaascore.core.reference import Reference
from amaascore.parties.party import Party
from amaascore.parties.children import Address, Email
from amaascore.tools.generate_party import generate_party, generate_address, generate_email


class PartyTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.party = generate_party()
        self.party_id = self.party.party_id

    def tearDown(self):
        pass

    def test_Party(self):
        self.assertEqual(type(self.party), Party)

    def test_PartyToDict(self):
        party_dict = self.party.__dict__
        self.assertEqual(type(party_dict), dict)
        self.assertEqual(party_dict.get('party_id'), self.party_id)

    def test_PartyToJSON(self):
        party_json = self.party.to_json()
        self.assertEqual(party_json.get('party_id'), self.party_id)
        # If party_json is valid JSON, this will run without serialisation errors
        json_party_id = json.loads(json.dumps(party_json, ensure_ascii=False)).get('party_id')
        self.assertEqual(json_party_id, self.party_id)

    def test_PartyEquality(self):
        party2 = copy.deepcopy(self.party)
        party3 = copy.deepcopy(self.party)
        party3.party_status = 'Inactive'
        self.assertEqual(self.party, party2)
        self.assertEqual(len({self.party, party2}), 1)
        self.assertEqual(len({self.party, party3}), 2)
        self.assertNotEqual(self.party, party3)

    def test_Children(self):
        address = list(self.party.addresses.values())[0]
        email = list(self.party.emails.values())[0]
        ref = list(self.party.references.values())[0]
        self.assertTrue(isinstance(address, Address))
        self.assertTrue(isinstance(email, Email))
        self.assertTrue(isinstance(ref, Reference))

    def test_Email(self):
        email = generate_email('test@amaas.com', email_primary=True)
        with self.assertRaisesRegexp(ValueError, 'Must set exactly one email as primary'):
            self.party.upsert_email('Test', email)
        email_type, email_value = list(self.party.emails.items())[0]
        email_value.email_primary = False
        with self.assertRaisesRegexp(ValueError, 'Must set exactly one email as primary'):
            self.party.upsert_email(email_type=email_type, email=email_value)

    def test_Address(self):
        address = generate_address(address_primary=True)
        with self.assertRaisesRegexp(ValueError, 'Must set exactly one address as primary'):
            self.party.upsert_address('Test', address)
        address_type, address_value = list(self.party.addresses.items())[0]
        address_value.address_primary = False
        with self.assertRaisesRegexp(ValueError, 'Must set exactly one address as primary'):
            self.party.upsert_address(address_type=address_type, address=address_value)

    def test_InvalidPartyStatus(self):
        with self.assertRaisesRegexp(ValueError, 'Invalid party status Invalid'):
            party = generate_party(party_status='Invalid')

if __name__ == '__main__':
    unittest.main()
