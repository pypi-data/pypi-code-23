from __future__ import absolute_import, division, print_function, unicode_literals

import copy
import json
import unittest

from amaascore.monitor.item import Item
from amaascore.tools.generate_monitor_item import generate_item


class ItemTest(unittest.TestCase):

    def setUp(self):
        self.longMessage = True  # Print complete error message on failure
        self.item = generate_item()
        self.item_id = self.item.item_id

    def tearDown(self):
        pass

    def test_Item(self):
        self.assertEqual(type(self.item), Item)

    def test_ItemToDict(self):
        item_dict = self.item.__dict__
        self.assertEqual(type(item_dict), dict)
        self.assertEqual(item_dict.get('item_id'), self.item_id)

    def test_ItemToJSON(self):
        item_json = self.item.to_json()
        self.assertEqual(item_json.get('item_id'), self.item_id)
        # If item_json is valid JSON, this will run without serialisation errors
        item_json_id = json.loads(json.dumps(item_json, ensure_ascii=False)).get('item_id')
        self.assertEqual(item_json_id, self.item_id)

if __name__ == '__main__':
    unittest.main()
