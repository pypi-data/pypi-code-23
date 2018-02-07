from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from amaascore.tools.generate_party import generate_address, generate_email


class PartyChildrenTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure

    def tearDown(self):
        pass

    def test_InvalidEmail(self):
        with self.assertRaisesRegexp(ValueError, 'Invalid email'):
            email = generate_email('invalid.email.amaas.com')

    def test_InvalidAddress(self):
        with self.assertRaisesRegexp(ValueError, 'Country ID should be a ISO 3166-1 Alpha-3 code'):
            address = generate_address(country_id='TEST')

if __name__ == '__main__':
    unittest.main()
