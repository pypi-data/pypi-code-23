# encoding: utf-8

import os
import sys
import json
import shutil
import unittest
from copy import deepcopy
from configurationutil import cfg_params, Configuration
from configurationutil.cfg_objects import cfg_item
from fdutil.path_tools import pop_path

# Register Config details (These are expected to be overwritten by an importing app)
cfg_params.APP_NAME = u'PyTestApp'
cfg_params.APP_AUTHOR = u'TEST'
cfg_params.APP_VERSION = u'1.0'

TEST_CONFIG = u'test_cfg_item'
TEST_KEY = u'name'
TEST_TEMPLATE = os.path.join(pop_path(__file__), u'..', u'resources', u'cfg_item_template.json')


def register_test_config():

    # Retrieve configuration instance
    cfg = Configuration()

    # Register configuration
    cfg.register(config=TEST_CONFIG,
                 config_type=cfg_params.CONST.json,
                 template=TEST_TEMPLATE)

    return cfg


class TestCfgItem(unittest.TestCase):

    CFG_ITEM = cfg_item.CfgItem

    TEST_KEY = TEST_KEY
    TEST_CONFIG = TEST_CONFIG

    FILE_EXT = cfg_params.CONST.json

    EXPECTED_STRING = (u"dummy: some_data\n"
                       u"dummy_dict: {u'a': 1, u'c': 3, u'b': 2}\n"
                       u"dummy_list: [u'item1', u'item2', u'item3']\n"
                       u"name: cfg1"
                       if sys.version_info[0] < 3 else
                       u"dummy: some_data\n"
                       u"dummy_dict: {'a': 1, 'b': 2, 'c': 3}\n"
                       u"dummy_list: ['item1', 'item2', 'item3']\n"
                       u"name: cfg1")

    @classmethod
    def setUpClass(cls):
        # this method copied from https://bl.ocks.org/twolfson/55f34dab606650a704d3
        """On inherited classes, run our `setUp` and `tearDown` method"""
        # Inspired via
        # http://stackoverflow.com/questions/1323455/python-unit-test-with-base-and-sub-class/17696807#17696807
        #  noqa
        if cls != TestCfgItem and cls.setUp != TestCfgItem.setUp:
            orig_set_up = cls.setUp

            def set_up_override(self):
                TestCfgItem.setUp(self)
                return orig_set_up(self)

            cls.setUp = set_up_override

        if cls != TestCfgItem and cls.tearDown != TestCfgItem.tearDown:
            orig_tear_down = cls.tearDown

            def tear_down_override(self):
                ret_val = orig_tear_down(self)
                TestCfgItem.tearDown(self)
                return ret_val

            cls.tearDown = tear_down_override

    @staticmethod
    def cfg_fn():
        return register_test_config()

    @staticmethod
    def file_reader(fp):
        return json.load(fp)

    def setUp(self):
        self.cfg = Configuration()
        self.cfg.__init__()  # Calling this here to ensure config re-inited following deletion in cleanup!

        self.cleanup_path = pop_path(pop_path(self.cfg.config_path)) + os.sep
        self.addCleanup(self.clean)

        self.parameters_cfg1 = {
            u'name': u'cfg1',
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

        self.parameters_cfg1_expected = deepcopy(self.parameters_cfg1)
        del self.parameters_cfg1_expected[u'name']

        self.new_dummy = u'different_data'
        self.new_list = [
            u'new_item'
        ]
        self.new_dict = {
            u'zzz': 999
        }

        # Expected data
        self.expected_file_state = {
            u'cfg1': deepcopy(self.parameters_cfg1_expected)
        }

        updated_parameters = deepcopy(self.parameters_cfg1_expected)
        updated_parameters[u'dummy'] = self.new_dummy
        self.expected_updated_file_state = {
            u'cfg1': updated_parameters
        }

        self.new_key = u'new_cfg_key'
        self.expected_updated_file_state_new_key = {
            self.new_key: deepcopy(self.parameters_cfg1_expected)
        }

        self.expected_len = 4
        self.expected_param_dict = self.parameters_cfg1

        self.overide_params = {
            u'dummy': u'this_got_overridden!',
            u'dummy_new': u'this wasn\'t here before'
        }
        self.expected_override = deepcopy(self.parameters_cfg1)
        self.expected_override[u'dummy'] = u'this_got_overridden!'
        self.expected_override[u'dummy_new'] = u'this wasn\'t here before'

    def tearDown(self):
        pass

    def clean(self):
        try:
            shutil.rmtree(self.cleanup_path)

        except OSError:
            pass

    def get_cfg_item(self,
                     params,
                     override=None):

        if override is None:
            override = {}

        return self.CFG_ITEM(cfg_fn=self.cfg_fn,
                             cfg_root=self.TEST_CONFIG,
                             key=params[self.TEST_KEY],
                             key_name=self.TEST_KEY,
                             **override)

    def get_item1(self,
                  override=None):
        return self.get_cfg_item(self.parameters_cfg1,
                                 override)

    def test_instantiation(self):
        self.get_item1()

    def test_name(self):
        item = self.get_item1()

        self.assertEqual(self.parameters_cfg1[self.TEST_KEY], item.name, u'CfgItem name incorrect')

    def test_key(self):
        item = self.get_item1()

        self.assertEqual(self.parameters_cfg1[self.TEST_KEY], item.key, u'CfgItem key incorrect')

    def test_parameters(self):
        item = self.get_item1()

        self.assertEqual(self.parameters_cfg1,
                         item.parameters,
                         u'CfgItem parameters incorrect')

        self.assertEqual(self.expected_param_dict[u'dummy'],
                         item.dummy,
                         u'CfgItem dummy attribute incorrect')
        self.assertEqual(self.expected_param_dict[u'dummy_list'],
                         item.dummy_list,
                         u'CfgItem dummy_list attribute incorrect')
        self.assertEqual(self.expected_param_dict[u'dummy_dict'],
                         item.dummy_dict,
                         u'CfgItem dummy_dict attribute incorrect')

        self.assertEqual(self.expected_param_dict[u'dummy'],
                         item[u'dummy'],
                         u'CfgItem dummy item incorrect')
        self.assertEqual(self.expected_param_dict[u'dummy_list'],
                         item[u'dummy_list'],
                         u'CfgItem dummy_list item incorrect')
        self.assertEqual(self.expected_param_dict[u'dummy_dict'],
                         item[u'dummy_dict'],
                         u'CfgItem dummy_dict item incorrect')

    def test_update_attribute(self):
        item = self.get_item1()

        item.dummy = self.new_dummy
        item.dummy_list = self.new_list
        item.dummy_dict = self.new_dict

        self.assertEqual(self.new_dummy, item.dummy, u'CfgItem update dummy attribute failed')
        self.assertEqual(self.new_dummy, item[u'dummy'], u'CfgItem update dummy item failed')
        self.assertEqual(self.new_list, item.dummy_list, u'CfgItem update list attribute failed')
        self.assertEqual(self.new_list, item[u'dummy_list'], u'CfgItem update list item failed')
        self.assertEqual(self.new_dict, item.dummy_dict, u'CfgItem update dict attribute failed')
        self.assertEqual(self.new_dict, item[u'dummy_dict'], u'CfgItem update dict item failed')

    def test_update_items(self):
        item = self.get_item1()

        item[u'dummy'] = self.new_dummy
        item[u'dummy_list'] = self.new_list
        item[u'dummy_dict'] = self.new_dict

        self.assertEqual(self.new_dummy, item.dummy, u'CfgItem update dummy attribute failed')
        self.assertEqual(self.new_dummy, item[u'dummy'], u'CfgItem update dummy item failed')
        self.assertEqual(self.new_list, item.dummy_list, u'CfgItem update list attribute failed')
        self.assertEqual(self.new_list, item[u'dummy_list'], u'CfgItem update list item failed')
        self.assertEqual(self.new_dict, item.dummy_dict, u'CfgItem update dict attribute failed')
        self.assertEqual(self.new_dict, item[u'dummy_dict'], u'CfgItem update dict item failed')

    def test_delete_attribute(self):
        item = self.get_item1()

        del item.dummy

        self.assertFalse(hasattr(item, u'dummy'), u'CfgItem delete attribute failed')
        self.assertNotIn(u'dummy', item, u'CfgItem delete attribute failed')
        self.assertNotIn(u'dummy', item._parameters, u'CfgItem delete attribute failed')

    def test_delete_item(self):
        item = self.get_item1()

        del item[u'dummy']

        self.assertFalse(hasattr(item, u'dummy'), u'CfgItem delete item failed')
        self.assertNotIn(u'dummy', item, u'CfgItem delete item failed')
        self.assertNotIn(u'dummy', item._parameters, u'CfgItem delete item failed')

    def test_iter_item(self):
        item = self.get_item1()

        params = []

        for param in item:
            params.append(param)
            self.assertIn(param, self.expected_param_dict, u'CfgItem iter failed')

        self.assertEqual(sorted(list(self.expected_param_dict.keys())), sorted(params), u'CfgItem iter failed')

    def test_len_item(self):
        item = self.get_item1()

        self.assertEqual(self.expected_len, len(item), u'CfgItem len(item) failed')

    def test_save_item(self):
        item = self.get_item1()

        # Update and confirm update
        item[u'dummy'] = self.new_dummy
        self.assertEqual(self.new_dummy, item.dummy, u'CfgItem update dummy attribute failed')
        self.assertEqual(self.new_dummy, item[u'dummy'], u'CfgItem update dummy item failed')

        # confirm file still matches unchanged values
        with open(os.path.join(self.cfg.config_path, u'{f}.{e}'.format(f=self.TEST_CONFIG,
                                                                       e=self.FILE_EXT)), u'r') as fp:
            raw_cfg_file = self.file_reader(fp)

        self.assertEqual(self.expected_file_state, dict(raw_cfg_file), u'CfgItem save updated item failed')

        # Now save and confirm
        item.save_changes()

        with open(os.path.join(self.cfg.config_path, u'{f}.{e}'.format(f=self.TEST_CONFIG,
                                                                       e=self.FILE_EXT)), u'r') as fp:
            raw_cfg_file = self.file_reader(fp)

        self.assertEqual(self.expected_updated_file_state, dict(raw_cfg_file), u'CfgItem save updated item failed')

    def test_save_item_new_key(self):
        item = self.get_item1()

        original_key = item.name
        new_key = self.new_key

        # Check original
        self.assertEqual(u'cfg1', original_key, u'original item key incorrect')

        # Make update
        item.name = new_key

        # confirm file still matches unchanged values
        with open(os.path.join(self.cfg.config_path, u'{f}.{e}'.format(f=self.TEST_CONFIG,
                                                                       e=self.FILE_EXT)), u'r') as fp:
            raw_cfg_file = self.file_reader(fp)

        self.assertEqual(self.expected_file_state, dict(raw_cfg_file), u'CfgItem save updated item failed')

        item.save_changes()

        # Check update
        self.assertEqual(new_key, item.name, u'new item key incorrect')

        with open(os.path.join(self.cfg.config_path, u'{f}.{e}'.format(f=self.TEST_CONFIG,
                                                                       e=self.FILE_EXT)), u'r') as fp:
            raw_cfg_file = self.file_reader(fp)

        self.assertEqual(self.expected_updated_file_state_new_key,
                         dict(raw_cfg_file),
                         u'CfgItem save updated item failed')

    def test_str(self):
        item = self.get_item1()

        self.assertEqual(self.EXPECTED_STRING, str(item), u'CfgItem str incorrect')

    def test_override(self):
        item = self.get_item1(override=self.overide_params)

        self.assertEqual(self.expected_override, dict(item), u'CfgItem override failed')


if __name__ == u'__main__':
    unittest.main()
