# encoding: utf-8

import os
import sys
import json
import unittest
from copy import deepcopy
from configurationutil import cfg_params
from configurationutil.cfg_objects.inheritable_cfg_item import InheritableCfgItem
from fdutil.parse_yaml import get_default_yaml_instance
from configurationutil.unittests.test_cfg_objects.inheritable_objects import (register_test_json_config,
                                                                              register_test_json_config_strict,
                                                                              ExampleItemsJSON,
                                                                              ExampleInheritableJSONItem,
                                                                              ExampleItemsJSONStrict,
                                                                              ExampleInheritableItemJSONStrict,
                                                                              TEST_KEY,
                                                                              TEST_JSON_CONFIG,
                                                                              TEST_JSON_CONFIG_STRICT,
                                                                              TEST_DEFAULT_PARAMS,
                                                                              register_test_yaml_config,
                                                                              register_test_yaml_config_strict,
                                                                              ExampleItemsYAML,
                                                                              ExampleInheritableYAMLItem,
                                                                              ExampleItemsYAMLStrict,
                                                                              ExampleInheritableItemYAMLStrict,
                                                                              TEST_YAML_CONFIG,
                                                                              TEST_YAML_CONFIG_STRICT)
from configurationutil.unittests.test_cfg_objects.test_cfg_item import TestCfgItem


TEST_FILE_TYPE = cfg_params.CONST.json
TEST_LOADER = json.load


class TestJSONInheritableCfgItemStrict(TestCfgItem):

    CFG_ITEMS = ExampleItemsJSONStrict
    CFG_ITEM = ExampleInheritableItemJSONStrict

    TEST_CONFIG = TEST_JSON_CONFIG_STRICT

    EXPECTED_STRING = (u"dummy: some_data\n"
                       u"dummy_dict: {u'a': 1, u'c': 3, u'b': 2}\n"
                       u"dummy_list: [u'item1', u'item2', u'item3']"
                       if sys.version_info[0] < 3 else
                       u"dummy: some_data\n"
                       u"dummy_dict: {'a': 1, 'b': 2, 'c': 3}\n"
                       u"dummy_list: ['item1', 'item2', 'item3']")

    @staticmethod
    def cfg_fn():
        return register_test_json_config_strict()

    def setUp(self):
        super(TestJSONInheritableCfgItemStrict, self).setUp()

        self.parameters_cfg1 = {
            u'name': u'cfg1',
            u'defaults': {
                u'dummy': u'some_data',
                u'dummy_list': [
                    u'item1',
                    u'item2',
                    u'item3'
                ],
                u'dummy_dict': {
                    u'a': 1,
                    u'b': 2,
                    u'c': 3
                }
            }
        }

        self.parameters_cfg1_expected = deepcopy(self.parameters_cfg1)
        del self.parameters_cfg1_expected[u'name']

        self.parameters_cfg3 = {
            u'name': u'cfg3',
            u'hidden': True,
            u'inherits': u'cfg1',
            u'defaults': {
                u'dummy_list': [
                    u'item2'
                ],
                u'dummy_dict': {
                    u'b': 9
                }
            }
        }

        self.parameters_cfg3_expected = deepcopy(self.parameters_cfg3)
        del self.parameters_cfg3_expected[u'name']

        self.expected_file_state = {
            u'cfg1': deepcopy(self.parameters_cfg1_expected),
            u'cfg3': deepcopy(self.parameters_cfg3_expected)
        }

        updated_parameters = deepcopy(self.parameters_cfg1_expected)
        updated_parameters[InheritableCfgItem.DEFAULTS][u'dummy'] = self.new_dummy
        self.expected_updated_file_state = {
            u'cfg1': updated_parameters,
            u'cfg3': deepcopy(self.parameters_cfg3_expected)
        }

        self.expected_len = 3
        self.expected_param_dict = self.parameters_cfg1[InheritableCfgItem.DEFAULTS]

        self.new_key = u'new_cfg_key'
        self.expected_updated_file_state_new_key = {
            self.new_key: deepcopy(self.parameters_cfg1_expected),
            u'cfg3': deepcopy(self.parameters_cfg3_expected)
        }

        self.expected_override = deepcopy(self.parameters_cfg1[InheritableCfgItem.DEFAULTS])
        self.expected_override[u'dummy'] = u'this_got_overridden!'
        self.expected_override[u'dummy_new'] = u'this wasn\'t here before'

    def get_item3(self):
        return self.CFG_ITEM(cfg_fn=self.cfg_fn,
                             cfg_root=self.TEST_CONFIG,
                             key=self.parameters_cfg3[self.TEST_KEY],
                             key_name=self.TEST_KEY)

    def test_hidden(self):
        item1 = self.get_item1()
        item3 = self.get_item3()

        self.assertFalse(item1.hidden, u'CfgItem hidden incorrect')
        self.assertTrue(item3.hidden, u'CfgItem hidden incorrect')


class TestJSONInheritableCfgItem(TestJSONInheritableCfgItemStrict):

    CFG_ITEMS = ExampleItemsJSON
    CFG_ITEM = ExampleInheritableJSONItem

    TEST_CONFIG = TEST_JSON_CONFIG

    EXPECTED_STRING = (u"dummy: some_data\n"
                       u"dummy_dict: {u'a': 1, u'c': 3, u'b': 2}\n"
                       u"dummy_extra: 123\n"
                       u"dummy_list: [u'item1', u'item2', u'item3']"
                       if sys.version_info[0] < 3 else
                       u"dummy: some_data\n"
                       u"dummy_dict: {'a': 1, 'b': 2, 'c': 3}\n"
                       u"dummy_extra: 123\n"
                       u"dummy_list: ['item1', 'item2', 'item3']")

    @staticmethod
    def cfg_fn():
        return register_test_json_config()

    def setUp(self):
        super(TestJSONInheritableCfgItemStrict, self).setUp()

        self.test_key = TEST_KEY

        self.parameters_cfg1 = {
            u'name': u'cfg1',
            u'defaults': {
                u'dummy': u'some_data',
                u'dummy_list': [
                    u'item1',
                    u'item2',
                    u'item3'
                ],
                u'dummy_dict': {
                    u'a': 1,
                    u'b': 2,
                    u'c': 3
                }
            }
        }

        self.parameters_cfg1_expected = deepcopy(self.parameters_cfg1)
        del self.parameters_cfg1_expected[u'name']

        self.parameters_cfg3 = {
            u'name': u'cfg3',
            u'hidden': True,
            u'inherits': u'cfg1',
            u'defaults': {
                u'dummy_list': [
                    u'item2'
                ],
                u'dummy_dict': {
                    u'b': 9
                }
            }
        }

        self.parameters_cfg3_expected = deepcopy(self.parameters_cfg3)
        del self.parameters_cfg3_expected[u'name']

        self.expected_file_state = {
            u'cfg1': deepcopy(self.parameters_cfg1_expected),
            u'cfg3': deepcopy(self.parameters_cfg3_expected)
        }

        updated_parameters = deepcopy(self.parameters_cfg1_expected)
        updated_parameters[InheritableCfgItem.DEFAULTS][u'dummy'] = self.new_dummy
        self.expected_updated_file_state = {
            u'cfg1': updated_parameters,
            u'cfg3': deepcopy(self.parameters_cfg3_expected)
        }

        self.expected_len = 4
        self.expected_param_dict = deepcopy(self.parameters_cfg1[InheritableCfgItem.DEFAULTS])
        self.expected_param_dict[u'dummy_extra'] = TEST_DEFAULT_PARAMS[u'dummy_extra']

        self.new_key = u'new_cfg_key'
        self.expected_updated_file_state_new_key = {
            self.new_key: deepcopy(self.parameters_cfg1_expected),
            u'cfg3': deepcopy(self.parameters_cfg3_expected)
        }

        self.expected_override = deepcopy(self.expected_param_dict)
        self.expected_override[u'dummy'] = u'this_got_overridden!'
        self.expected_override[u'dummy_new'] = u'this wasn\'t here before'

    def test_delete_attribute(self):
        item = self.get_item1()

        self.assertEqual(self.parameters_cfg1[InheritableCfgItem.DEFAULTS][u'dummy'],
                         item.dummy,
                         u'CfgItem delete item failed')

        del item.dummy

        # Should clear the value and thus the default is returned!

        self.assertTrue(hasattr(item, u'dummy'), u'CfgItem delete attribute failed')
        self.assertIn(u'dummy', item, u'CfgItem delete attribute failed')
        self.assertNotIn(u'dummy', item._parameters, u'CfgItem delete attribute failed')
        self.assertEqual(TEST_DEFAULT_PARAMS[u'dummy'], item.dummy, u'CfgItem delete attribute failed')

    def test_delete_item(self):
        item = self.get_item1()

        self.assertEqual(self.parameters_cfg1[InheritableCfgItem.DEFAULTS][u'dummy'],
                         item.dummy,
                         u'CfgItem delete item failed')

        del item[u'dummy']

        # Should clear the value and thus the default is returned!

        self.assertTrue(hasattr(item, u'dummy'), u'CfgItem delete item failed')
        self.assertIn(u'dummy', item, u'CfgItem delete item failed')
        self.assertNotIn(u'dummy', item._parameters, u'CfgItem delete item failed')
        self.assertEqual(TEST_DEFAULT_PARAMS[u'dummy'], item.dummy, u'CfgItem delete item failed')

    def test_del_save_item(self):
        # We basically don't want to see any inherited or DEFAULT_VALUES propagated
        # into the file for this item

        item = self.get_item1()

        # Confirm values before
        self.assertEqual(self.parameters_cfg1[InheritableCfgItem.DEFAULTS][u'dummy'],
                         item.dummy,
                         u'CfgItem update dummy attribute failed')
        self.assertEqual(self.parameters_cfg1[InheritableCfgItem.DEFAULTS][u'dummy'],
                         item[u'dummy'],
                         u'CfgItem update dummy item failed')

        # confirm file still matches unchanged values
        with open(os.path.join(self.cfg.config_path, u'{f}.{e}'.format(f=self.TEST_CONFIG,
                                                                       e=self.FILE_EXT)), u'r') as fp:
            raw_cfg_file = self.file_reader(fp)

        self.assertEqual(self.expected_file_state, dict(raw_cfg_file), u'CfgItem save updated item failed')

        del item[u'dummy']

        # Now save and confirm
        item.save_changes()

        with open(os.path.join(self.cfg.config_path, u'{f}.{e}'.format(f=self.TEST_CONFIG,
                                                                       e=self.FILE_EXT)), u'r') as fp:
            raw_cfg_file = self.file_reader(fp)

        updated_state = deepcopy(self.expected_updated_file_state)
        del updated_state[u'cfg1'][InheritableCfgItem.DEFAULTS][u'dummy']

        self.assertEqual(updated_state, dict(raw_cfg_file), u'CfgItem save updated item failed')


class TestYAMLInheritableCfgItemStrict(TestJSONInheritableCfgItemStrict):

    CFG_ITEMS = ExampleItemsYAMLStrict
    CFG_ITEM = ExampleInheritableItemYAMLStrict

    TEST_CONFIG = TEST_YAML_CONFIG_STRICT

    FILE_EXT = cfg_params.CONST.yaml

    EXPECTED_STRING = (u"dummy: some_data\n"
                       u"dummy_dict: {'a': 1, 'c': 3, 'b': 2}\n"
                       u"dummy_list: ['item1', 'item2', 'item3']"
                       if sys.version_info[0] < 3 else
                       u"dummy: some_data\n"
                       u"dummy_dict: {'a': 1, 'b': 2, 'c': 3}\n"
                       u"dummy_list: ['item1', 'item2', 'item3']")

    # Once Comment YAML performance issue fixed and merged back into yaml provider
    # re-enable this expected string:

    #EXPECTED_STRING = (u"dummy: some_data\n"
    #                   u"dummy_dict: ordereddict([('a', 1), ('b', 2), ('c', 3)])\n"
    #                   u"dummy_list: ['item1', 'item2', 'item3']"
    #                   if sys.version_info[0] < 3 else
    #                   u"dummy: some_data\n"
    #                   u"dummy_dict: CommentedMap([('a', 1), ('b', 2), ('c', 3)])\n"
    #                   u"dummy_list: ['item1', 'item2', 'item3']")

    @staticmethod
    def cfg_fn():
        return register_test_yaml_config_strict()

    @staticmethod
    def file_reader(fp):
        yaml = get_default_yaml_instance()
        return yaml.load(fp)


class TestYAMLInheritableCfgItem(TestJSONInheritableCfgItem):

    CFG_ITEMS = ExampleItemsYAML
    CFG_ITEM = ExampleInheritableYAMLItem

    TEST_CONFIG = TEST_YAML_CONFIG

    FILE_EXT = cfg_params.CONST.yaml

    EXPECTED_STRING = (u"dummy: some_data\n"
                       u"dummy_dict: {'a': 1, 'c': 3, 'b': 2}\n"
                       u"dummy_extra: 123\n"
                       u"dummy_list: ['item1', 'item2', 'item3']"
                       if sys.version_info[0] < 3 else
                       u"dummy: some_data\n"
                       u"dummy_dict: {'a': 1, 'b': 2, 'c': 3}\n"
                       u"dummy_extra: 123\n"
                       u"dummy_list: ['item1', 'item2', 'item3']")

    # Once Comment YAML performance issue fixed and merged back into yaml provider
    # re-enable this expected string:

    #EXPECTED_STRING = (u"dummy: some_data\n"
    #                   u"dummy_dict: ordereddict([('a', 1), ('b', 2), ('c', 3)])\n"
    #                   u"dummy_extra: 123\n"
    #                   u"dummy_list: ['item1', 'item2', 'item3']"
    #                   if sys.version_info[0] < 3 else
    #                   u"dummy: some_data\n"
    #                   u"dummy_dict: CommentedMap([('a', 1), ('b', 2), ('c', 3)])\n"
    #                   u"dummy_extra: 123\n"
    #                   u"dummy_list: ['item1', 'item2', 'item3']")

    @staticmethod
    def cfg_fn():
        return register_test_yaml_config()

    @staticmethod
    def file_reader(fp):
        yaml = get_default_yaml_instance()
        return yaml.load(fp)


if __name__ == u'__main__':
    unittest.main()
