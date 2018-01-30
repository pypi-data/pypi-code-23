# coding=utf-8
import unittest
from mailchimp.objects import MCLocation


class TestMCLocation(unittest.TestCase):
    def get_location(self):
        return {
            'latitude': 'Latitude value',
            'longitude': 'Longitude value',
            'gmtoff': 'Gmtoff value',
            'dstoff': 'Dstoff value',
            'country_code': 'Country code value',
            'timezone': 'Timezone value'
        }

    def test_item_url(self):
        location = MCLocation()
        self.assertIsNone(location.item_url)

    def test_valid_search_params(self):
        location = MCLocation()
        self.assertEqual(['offset', 'count', 'fields', 'exclude_fields'],
                         location.valid_search_params)

    def test_none_init(self):
        location = MCLocation(None)

        for prop in ['latitude', 'longitude', 'gmtoff', 'dstoff', 'country_code', 'timezone']:
            self.assertIsNone(getattr(location, prop))

    def test_empty_init(self):
        location = MCLocation()

        for prop in ['latitude', 'longitude', 'gmtoff', 'dstoff', 'country_code', 'timezone']:
            self.assertIsNone(getattr(location, prop))

    def test_init(self):
        location = MCLocation(self.get_location())

        self.assertEqual('Latitude value', location.latitude)
        self.assertEqual('Longitude value', location.longitude)
        self.assertEqual('Gmtoff value', location.gmtoff)
        self.assertEqual('Dstoff value', location.dstoff)
        self.assertEqual('Country code value', location.country_code)
        self.assertEqual('Timezone value', location.timezone)

    def test_to_str(self):
        location = MCLocation(self.get_location())
        self.assertEqual('', str(location))

    def test_repr(self):
        location = MCLocation(self.get_location())
        self.assertEqual('<MCLocation: >', str(repr(location)))
