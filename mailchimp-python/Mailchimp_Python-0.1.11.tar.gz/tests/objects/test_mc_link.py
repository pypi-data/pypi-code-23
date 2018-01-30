# coding=utf-8
import unittest
from mailchimp.objects import MCLink


class TestMCLink(unittest.TestCase):
    def get_link(self):
        return {
            'rel': 'Rel value',
            'href': 'Href value',
            'method': 'Method value',
            'targetSchema': 'TargetSchema value'
        }

    def test_item_url(self):
        link = MCLink()
        self.assertIsNone(link.item_url)

    def test_valid_search_params(self):
        link = MCLink()
        self.assertEqual(['offset', 'count', 'fields', 'exclude_fields'],
                         link.valid_search_params)

    def test_none_init(self):
        link = MCLink(None)

        for prop in ['rel', 'href', 'method', 'targetSchema']:
            self.assertIsNone(getattr(link, prop))

    def test_empty_init(self):
        link = MCLink()

        for prop in ['rel', 'href', 'method', 'targetSchema']:
            self.assertIsNone(getattr(link, prop))

    def test_init(self):
        link = MCLink(self.get_link())

        self.assertEqual('Rel value', link.rel)
        self.assertEqual('Href value', link.href)
        self.assertEqual('Method value', link.method)
        self.assertEqual('TargetSchema value', link.targetSchema)

    def test_to_str(self):
        link = MCLink(self.get_link())
        self.assertEqual('', str(link))

    def test_repr(self):
        link = MCLink(self.get_link())
        self.assertEqual('<MCLink: >', str(repr(link)))
