# coding=utf-8
import unittest

from mailchimp.objects import MCContact


class TestMCContact(unittest.TestCase):
    def get_contact(self):
        return {
            'company': 'Company value',
            'address1': 'Address1 value',
            'address2': 'Address2 value',
            'city': 'City value',
            'state': 'State value',
            'zip': 'Zip value',
            'country': 'Country value',
            'phone': 'Phone value'
        }

    def test_item_url(self):
        contact = MCContact()
        self.assertIsNone(contact.item_url)

    def test_valid_search_params(self):
        contact = MCContact()
        self.assertEqual(['offset', 'count', 'fields', 'exclude_fields'],
                         contact.valid_search_params)

    def test_none_init(self):
        contact = MCContact(None)

        for prop in ['company', 'address1', 'address2', 'city', 'state', 'zip', 'country', 'phone']:
            self.assertIsNone(getattr(contact, prop))

    def test_empty_init(self):
        contact = MCContact()

        for prop in ['company', 'address1', 'address2', 'city', 'state', 'zip', 'country', 'phone']:
            self.assertIsNone(getattr(contact, prop))

    def test_init(self):
        contact = MCContact(self.get_contact())

        self.assertEqual('Company value', contact.company)
        self.assertEqual('Address1 value', contact.address1)
        self.assertEqual('Address2 value', contact.address2)
        self.assertEqual('City value', contact.city)
        self.assertEqual('State value', contact.state)
        self.assertEqual('Zip value', contact.zip)
        self.assertEqual('Country value', contact.country)
        self.assertEqual('Phone value', contact.phone)

    def test_to_str(self):
        contact = MCContact(self.get_contact())
        self.assertEqual('', str(contact))

    def test_repr(self):
        contact = MCContact(self.get_contact())
        self.assertEqual('<MCContact: >', str(repr(contact)))
