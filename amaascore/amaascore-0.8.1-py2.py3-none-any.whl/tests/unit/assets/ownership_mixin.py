from datetime import date
from decimal import Decimal
import random
import unittest

from amaascore.tools.generate_real_asset import generate_wine


class OwnershipMixinTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message
        self.client_id = random.randint(1, 2**31-1)
        self.asset_manager_id = random.randint(1, 2**31-1)
        self.wine = generate_wine()

    def tearDown(self):
        pass

    def test_Ownership(self):
        self.wine.ownership = [{'party_id': 'XYZ', 'split': Decimal('1')}]

    def test_OwnershipType(self):
        with self.assertRaisesRegexp(TypeError, 'ownership must be a list of dictionaries'):
            self.wine.ownership = {'party_id': 'XYZ', 'split': Decimal('1')}
        with self.assertRaisesRegexp(TypeError, 'ownership must be a list of dictionaries'):
            self.wine.ownership = [Decimal('0.5'), Decimal('0.5')]

    def test_OwnershipSum(self):
        with self.assertRaisesRegexp(ValueError, 'Ownership must sum up to 100%'):
            self.wine.ownership = [{'party_id': 'XYZ', 'split': Decimal('0.4')},
                                   {'party_id': 'XYZ', 'split': Decimal('0.5')}]

    def test_OwnershipMandatoryValues(self):
        with self.assertRaisesRegexp(ValueError, 'Ownership missing one or more party_ids'):
            self.wine.ownership = [{'split': Decimal('0.5')},
                                   {'party_id': 'XYZ', 'split': Decimal('0.5')}]
        with self.assertRaisesRegexp(ValueError, 'Ownership missing one or more splits'):
            self.wine.ownership = [{'party_id': 'XYZ'},
                                   {'party_id': 'XYZ', 'split': Decimal('0.5')}]

if __name__ == '__main__':
    unittest.main()
