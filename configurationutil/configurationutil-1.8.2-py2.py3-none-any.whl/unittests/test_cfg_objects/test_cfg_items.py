# encoding: utf-8

import os
import shutil
import unittest
from copy import deepcopy
from configurationutil import cfg_params, Configuration
from configurationutil.cfg_objects import cfg_items, cfg_item
from fdutil.path_tools import pop_path

# Register Config details (These are expected to be overwritten by an importing app)
cfg_params.APP_NAME = u'PyTestApp'
cfg_params.APP_AUTHOR = u'TEST'
cfg_params.APP_VERSION = u'1.0'

TEST_CONFIG = u'test_cfg_items'
TEST_KEY = u'name'
TEST_TEMPLATE = os.path.join(pop_path(__file__), u'..', u'resources', u'cfg_items_template.json')


def register_test_config():

    # Retrieve configuration instance
    cfg = Configuration()

    # Register configuration
    cfg.register(config=TEST_CONFIG,
                 config_type=cfg_params.CONST.json,
                 template=TEST_TEMPLATE)

    return cfg


class TestCfgItems(unittest.TestCase):

    CFG_ITEMS = cfg_items.CfgItems

    TEST_KEY = TEST_KEY
    TEST_CONFIG = TEST_CONFIG

    @staticmethod
    def cfg_fn():
        return register_test_config()

    def setUp(self):
        self.cfg = Configuration()
        self.cfg.__init__()  # Calling this here to ensure config re-inited following deletion in cleanup!

        self.cleanup_path = pop_path(pop_path(self.cfg.config_path)) + os.sep
        self.addCleanup(self.clean)

        self.cfg1 = {
            'dummy': 'some_data',
            'dummy_list': ['item1', 'item2', 'item3'],
            'dummy_dict': {'a': 1, 'b': 2, 'c': 3}
        }
        self.cfg2 = {
            'dummy': 'some_more_data',
            'dummy_list': ['item4', 'item5', 'item6'],
            'dummy_dict': {'a': 4, 'b': 5, 'c': 6}
        }
        self.cfg3 = {
            'dummy': 'some_extra_data',
            'dummy_list': ['item7', 'item8', 'item9'],
            'dummy_dict': {'a': 7, 'b': 8, 'c': 9}
        }

        self.raw = {
            u'cfg1': self.cfg1,
            u'cfg2': self.cfg2,
            u'cfg3': self.cfg3
        }

        self.default = {
            u'cfg1': self.cfg1,
            u'cfg2': self.cfg2,
            u'cfg3': self.cfg3
        }

        self.new_key = u'cfg_new'
        self.new_data = {
            u'data': u'new_data!'
        }

        self.del_key = u'cfg3'

        self.item_by_key_key = u'dummy'
        self.item_by_key_value = u'some_extra_data'

        self.get_item_name = u'cfg2'

    def tearDown(self):
        pass

    def clean(self):
        try:
            shutil.rmtree(self.cleanup_path)

        except OSError:
            pass

    def get_cfg_items(self):
        return self.CFG_ITEMS(cfg_fn=self.cfg_fn,
                              cfg_root=self.TEST_CONFIG,
                              key_name=self.TEST_KEY)

    def validate_item_list(self,
                           items,
                           add=False,
                           delete=False):

        name_list = list(self.default.keys())

        if add:
            name_list.append(self.new_key)
            self.default[self.new_key] = self.new_data

        if delete:
            name_list.remove(self.del_key)
            del self.default[self.del_key]

        for item in items:
            self.assertTrue(isinstance(item, cfg_item.CfgItem), u'Check item type failed')
            self.assertIn(item[self.TEST_KEY], name_list, u'Item not in config')

            for param in item:
                if not param == self.TEST_KEY:
                    self.assertEqual(self.default[item[self.TEST_KEY]][param],
                                     item[param],
                                     u'Item does not match config')

    def validate_items(self,
                       items):

        self.assertTrue(isinstance(items, list), u'CfgItems get items type failed')
        self.assertEqual(len(self.default), len(items), u'CfgItems get items length failed')

        self.validate_item_list(items=items)

    def validate_item(self,
                      item):

        expected_item = deepcopy(self.cfg2)
        expected_item[self.TEST_KEY] = u'cfg2'

        self.assertEqual(expected_item, item, u'CfgItems get item failed')

    # Tests
    def test_instantiation(self):
        self.get_cfg_items()

    def test_raw_items(self):
        items = self.get_cfg_items()

        self.assertEqual(self.raw, items.raw_items, u'CfgItems get raw items failed')

    def test_iter(self):
        items = self.get_cfg_items()

        self.validate_item_list(items=items)

    def test_load_item(self):
        items = self.get_cfg_items()

        item = items.load_item(self.get_item_name)

        self.assertTrue(isinstance(item, cfg_item.CfgItem))
        self.assertTrue(isinstance(item, items._item_class))
        self.validate_item(item)

    def test_get_items(self):
        items = self.get_cfg_items()

        self.validate_items(items=items.get_items())

    def test_get_items_active_only(self):
        items = self.get_cfg_items()

        self.validate_items(items=items.get_items(active_only=True))

    def test_get_active_items(self):
        items = self.get_cfg_items()

        self.validate_items(items=items.get_active_items())

    def test_get_item(self):
        items = self.get_cfg_items()

        self.validate_item(items.get_item(self.get_item_name))

    def test_get_item_obj(self):
        items = self.get_cfg_items()

        item_obj = items.get_item(self.get_item_name)

        self.validate_item(items.get_item(item_obj))

    def test_get_item_active_only(self):
        items = self.get_cfg_items()

        self.validate_item(items.get_item(self.get_item_name, active_only=True))

    def test_get_item_suppress_refetch(self):
        items = self.get_cfg_items()

        item_obj = items.get_item(self.get_item_name)

        self.validate_item(items.get_item(item_obj, suppress_refetch=True))

    def test_get_item_by_key(self):
        items = self.get_cfg_items()

        self.validate_item_list([items.get_item_by_key(self.item_by_key_key, self.item_by_key_value)])

    def test_add(self):
        items = self.get_cfg_items()

        items.add(key_attr=self.new_key,
                  config=self.new_data)

        self.validate_item_list([items.get_item(self.new_key)],
                                add=True)

    def test_delete(self):
        items = self.get_cfg_items()

        items.delete(key_attr=self.del_key)

        self.validate_item_list(items.get_items(),
                                delete=True)


if __name__ == u'__main__':
    unittest.main()

# TODO: test has_active
# TODO: test item_class
