# encoding: utf-8

import unittest
from configurationutil.cfg_objects import cfg_item
from configurationutil.unittests.test_cfg_objects.inheritable_objects import (
    register_test_json_items_config,
    register_test_json_items_config_strict,
    ExampleItemsJSON,
    ExampleInheritableJSONItem,
    ExampleItemsJSONStrict,
    ExampleItemsJSONRecursive,
    register_test_yaml_items_config,
    register_test_yaml_items_config_strict,
    ExampleItemsYAML,
    ExampleItemsYAMLStrict,
    ExampleItemsYAMLRecursive,
    TEST_KEY
)
from configurationutil.unittests.test_cfg_objects.test_cfg_items import TestCfgItems


class TestJSONInheritableCfgItemsStrict(TestCfgItems):

    CFG_ITEMS = ExampleItemsJSONStrict

    TEST_KEY = TEST_KEY

    @staticmethod
    def cfg_fn():
        return register_test_json_items_config_strict()

    def setUp(self):
        super(TestJSONInheritableCfgItemsStrict, self).setUp()

        self.cfg1 = {
            'defaults': {
                'dummy': 'some_data',
                'dummy_list': [
                    'item1',
                    'item2',
                    'item3'
                ],
                'dummy_dict': {
                    'a': 1,
                    'b': 2,
                    'c': 3
                }
            }
        }
        self.cfg2 = {
            'hidden': True,
            'inherits': 'cfg1',
            'defaults': {
                'dummy_list': [
                    'item2'
                ],
                'dummy_dict': {
                    'b': 999
                }
            }
        }
        self.cfg2_expected = {
            'hidden': True,
            'inherits': 'cfg1',
            'defaults': {
                'dummy': 'some_data',
                'dummy_list': [
                    'item2'
                ],
                'dummy_dict': {
                    'b': 999
                }
            }
        }
        self.cfg3 = None
        self.cfg3_expected = {}
        self.cfg4 = {
            'inherits': 'cfg2',
            'defaults': {
                'dummy': 'some_data_cfg_4',
            }
        }
        self.cfg4_expected = {
            'inherits': 'cfg2',
            'defaults': {
                'dummy': 'some_data_cfg_4',
                'dummy_list': [
                    'item2'
                ],
                'dummy_dict': {
                    'b': 999
                }
            }
        }
        self.cfg5 = {
            'inherits': 'cfg2',
            'defaults': {
                'dummy_dict': None
            }
        }
        self.cfg5_expected = {
            'inherits': 'cfg2',
            'defaults': {
                'dummy': 'some_data',
                'dummy_list': [
                    'item2'
                ],
                'dummy_dict': None
            }
        }

        self.raw = {
            u'cfg1': self.cfg1,
            u'cfg2': self.cfg2,
            u'cfg3': self.cfg3,
            u'cfg4': self.cfg4,
            u'cfg5': self.cfg5
        }

        self.default = {
            u'cfg1': self.cfg1,
            u'cfg3': self.cfg3_expected,
            u'cfg4': self.cfg4_expected,
            u'cfg5': self.cfg5_expected
        }

        self.new_key = u'cfg_new'
        self.new_data = {
            u'defaults': {
                u'dummy': u'new_data!'
            }
        }
        self.new_data_expected = {
            u'defaults': {
                u'dummy': u'new_data!'
            }
        }

        self.item_by_key_value = u'some_data_cfg_4'

        self.get_item_name = u'cfg4'

    def get_cfg_items(self):
        return self.CFG_ITEMS()

    def validate_item_list(self,
                           items,
                           add=False,
                           delete=False):

        name_list = list(self.default.keys())

        if add:
            name_list.append(self.new_key)
            self.default[self.new_key] = self.new_data_expected

        if delete:
            name_list.remove(self.del_key)
            del self.default[self.del_key]

        for item in items:
            self.assertTrue(isinstance(item, cfg_item.CfgItem), u'Check item type failed')
            self.assertIn(item[self.TEST_KEY], name_list, u'Item not in config')

            for param in item:
                if not param == self.TEST_KEY:
                    self.assertEqual(self.default[item[self.TEST_KEY]][ExampleInheritableJSONItem.DEFAULTS][param],
                                     item[param],
                                     u'Item does not match config')

    def validate_item(self,
                      item):

        expected_item = self.cfg4_expected[ExampleInheritableJSONItem.DEFAULTS]

        self.assertEqual(expected_item, item, u'CfgItems get item failed')

    def test_get_item(self):
        items = self.get_cfg_items()

        with self.assertRaises(LookupError):
            items.get_item(u'cfg2')

        super(TestJSONInheritableCfgItemsStrict, self).test_get_item()


class TestJSONInheritableCfgItems(TestJSONInheritableCfgItemsStrict):

    CFG_ITEMS = ExampleItemsJSON

    @staticmethod
    def cfg_fn():
        return register_test_json_items_config()

    def setUp(self):
        super(TestJSONInheritableCfgItems, self).setUp()

        self.cfg1 = {
            'defaults': {
                'dummy': 'some_data',
                'dummy_list': [
                    'item1',
                    'item2',
                    'item3'
                ],
                'dummy_dict': {
                    'a': 1,
                    'b': 2,
                    'c': 3
                }
            }
        }
        self.cfg1_expected = {
            'defaults': {
                'dummy': 'some_data',
                'dummy_list': [
                    'item1',
                    'item2',
                    'item3'
                ],
                'dummy_dict': {
                    'a': 1,
                    'b': 2,
                    'c': 3
                },
                'dummy_extra': 123
            }
        }
        self.cfg2 = {
            'hidden': True,
            'inherits': 'cfg1',
            'defaults': {
                'dummy_list': [
                    'item2'
                ],
                'dummy_dict': {
                    'b': 999
                }
            }
        }
        self.cfg2_expected = {
            'hidden': True,
            'inherits': 'cfg1',
            'defaults': {
                'dummy': 'some_data',
                'dummy_list': [
                    'item2'
                ],
                'dummy_dict': {
                    'b': 999
                },
                'dummy_extra': 123
            }
        }
        self.cfg3 = None
        self.cfg3_expected = {
            'defaults': {
                'dummy': '',
                'dummy_list': [],
                'dummy_dict': {},
                'dummy_extra': 123
            }
        }
        self.cfg4 = {
            'inherits': 'cfg2',
            'defaults': {
                'dummy': 'some_data_cfg_4',
            }
        }
        self.cfg4_expected = {
            'inherits': 'cfg2',
            'defaults': {
                'dummy': 'some_data_cfg_4',
                'dummy_list': [
                    'item2'
                ],
                'dummy_dict': {
                    'b': 999
                },
                'dummy_extra': 123
            }
        }
        self.cfg5 = {
            'inherits': 'cfg2',
            'defaults': {
                'dummy_dict': None
            }
        }
        self.cfg5_expected = {
            'inherits': 'cfg2',
            'defaults': {
                'dummy': 'some_data',
                'dummy_list': [
                    'item2'
                ],
                'dummy_dict': None,
                'dummy_extra': 123
            }
        }

        self.raw = {
            u'cfg1': self.cfg1,
            u'cfg2': self.cfg2,
            u'cfg3': self.cfg3,
            u'cfg4': self.cfg4,
            u'cfg5': self.cfg5
        }

        self.default = {
            u'cfg1': self.cfg1_expected,
            u'cfg3': self.cfg3_expected,
            u'cfg4': self.cfg4_expected,
            u'cfg5': self.cfg5_expected
        }

        self.new_data_expected = {
            u'defaults': {
                u'dummy': u'new_data!',
                u'dummy_list': [],
                u'dummy_dict': {},
                u'dummy_extra': 123
            }
        }

        self.item_by_key_value = u'some_data_cfg_4'

        self.get_item_name = u'cfg4'


class TestJSONInheritableCfgItemsRecursive(TestJSONInheritableCfgItemsStrict):

    CFG_ITEMS = ExampleItemsJSONRecursive

    def setUp(self):
        super(TestJSONInheritableCfgItemsStrict, self).setUp()

        self.cfg1 = {
            'defaults': {
                'dummy': 'some_data',
                'dummy_list': [
                    'item1',
                    'item2',
                    'item3'
                ],
                'dummy_dict': {
                    'a': 1,
                    'b': 2,
                    'c': 3
                }
            }
        }
        self.cfg2 = {
            'hidden': True,
            'inherits': 'cfg1',
            'defaults': {
                'dummy_list': [
                    'item2'
                ],
                'dummy_dict': {
                    'b': 999
                }
            }
        }
        self.cfg2_expected = {
            'hidden': True,
            'inherits': 'cfg1',
            'defaults': {
                'dummy': 'some_data',
                'dummy_list': [
                    'item2'
                ],
                'dummy_dict': {
                    'a': 1,
                    'b': 999,
                    'c': 3
                }
            }
        }
        self.cfg3 = None
        self.cfg3_expected = {}
        self.cfg4 = {
            'inherits': 'cfg2',
            'defaults': {
                'dummy': 'some_data_cfg_4',
            }
        }
        self.cfg4_expected = {
            'inherits': 'cfg2',
            'defaults': {
                'dummy': 'some_data_cfg_4',
                'dummy_list': [
                    'item2'
                ],
                'dummy_dict': {
                    'a': 1,
                    'b': 999,
                    'c': 3
                }
            }
        }
        self.cfg5 = {
            'inherits': 'cfg2',
            'defaults': {
                'dummy_dict': None
            }
        }
        self.cfg5_expected = {
            'inherits': 'cfg2',
            'defaults': {
                'dummy': 'some_data',
                'dummy_list': [
                    'item2'
                ],
                'dummy_dict': None
            }
        }

        self.raw = {
            u'cfg1': self.cfg1,
            u'cfg2': self.cfg2,
            u'cfg3': self.cfg3,
            u'cfg4': self.cfg4,
            u'cfg5': self.cfg5
        }

        self.default = {
            u'cfg1': self.cfg1,
            u'cfg3': self.cfg3_expected,
            u'cfg4': self.cfg4_expected,
            u'cfg5': self.cfg5_expected
        }

        self.new_key = u'cfg_new'
        self.new_data = {
            u'defaults': {
                u'dummy': u'new_data!'
            }
        }
        self.new_data_expected = {
            u'defaults': {
                u'dummy': u'new_data!'
            }
        }

        self.item_by_key_value = u'some_data_cfg_4'

        self.get_item_name = u'cfg4'


class TestYAMLInheritableCfgItemsStrict(TestJSONInheritableCfgItemsStrict):

    CFG_ITEMS = ExampleItemsYAMLStrict

    @staticmethod
    def cfg_fn():
        return register_test_yaml_items_config_strict()


class TestYAMLInheritableCfgItems(TestJSONInheritableCfgItems):

    CFG_ITEMS = ExampleItemsYAML

    @staticmethod
    def cfg_fn():
        return register_test_yaml_items_config()


class TestYAMLInheritableCfgItemsRecursive(TestJSONInheritableCfgItemsRecursive):

    CFG_ITEMS = ExampleItemsYAMLRecursive


if __name__ == u'__main__':
    unittest.main()
