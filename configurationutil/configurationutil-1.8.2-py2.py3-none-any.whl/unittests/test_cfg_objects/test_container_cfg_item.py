# encoding: utf-8

import os
import json
import shutil
import unittest
from fdutil.path_tools import pop_path
from configurationutil import cfg_params, Configuration
from fdutil.parse_yaml import get_default_yaml_instance
from configurationutil.unittests.test_cfg_objects.container_objects import (register_test_json_config,
                                                                            register_test_yaml_config,
                                                                            ExampleContainerJSONItem,
                                                                            ExampleContainerYAMLItem,
                                                                            ExampleItemsJSON,
                                                                            ExampleItemsYAML,
                                                                            TEST_JSON_CONFIG,
                                                                            TEST_YAML_CONFIG)

TEST_FILE_TYPE = cfg_params.CONST.json
TEST_LOADER = json.load


class TestJSONContainerCfgItem(unittest.TestCase):

    CFG_ITEMS = ExampleItemsJSON
    CFG_ITEM = ExampleContainerJSONItem

    TEST_CONFIG = TEST_JSON_CONFIG
    TEST_CONTAINER_KEY = u'container1'
    TEST_CONTAINER2_KEY = u'container2'

    EXPECTED_STRING = (u"dummy: some_data\n"
                       u"dummy_dict: {u'a': 1, u'c': 3, u'b': 2}\n"
                       u"dummy_list: [u'item1', u'item2', u'item3']")

    @classmethod
    def setUpClass(cls):
        # this method copied from https://bl.ocks.org/twolfson/55f34dab606650a704d3
        """On inherited classes, run our `setUp` and `tearDown` method"""
        # Inspired via
        # http://stackoverflow.com/questions/1323455/python-unit-test-with-base-and-sub-class/17696807#17696807
        #  noqa
        if cls != TestJSONContainerCfgItem and cls.setUp != TestJSONContainerCfgItem.setUp:
            orig_set_up = cls.setUp

            def set_up_override(self):
                TestJSONContainerCfgItem.setUp(self)
                return orig_set_up(self)

            cls.setUp = set_up_override

        if cls != TestJSONContainerCfgItem and cls.tearDown != TestJSONContainerCfgItem.tearDown:
            orig_tear_down = cls.tearDown

            def tear_down_override(self):
                ret_val = orig_tear_down(self)
                TestJSONContainerCfgItem.tearDown(self)
                return ret_val

            cls.tearDown = tear_down_override

    @staticmethod
    def cfg_fn():
        return register_test_json_config()

    @staticmethod
    def file_reader(fp):
        return json.load(fp)

    def setUp(self):
        self.cfg = Configuration()
        self.cfg.__init__()  # Calling this here to ensure config re-inited following deletion in cleanup!

        self.cleanup_path = pop_path(pop_path(self.cfg.config_path)) + os.sep
        self.addCleanup(self.clean)

        self.container1 = {
            u'container1': {
                u'item_defaults': {
                    u'dummy': u'some_data_default'
                },
                u'items': {
                    u'cfg1': {
                        u'dummy': u'some_data_container1_cfg1'
                    },
                    u'cfg3': {
                        u'dummy_dict': {
                            u'b': 777
                        }
                    },
                    u'cfg4': None,
                    u'cfg5': u''
                }
            }
        }

        self.expected_len = 4

        self.expected_param_dict = {
            u'cfg1': {
                u'dummy': u'some_data_container1_cfg1',
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
            },
            u'cfg3': {
                u'dummy': u'some_data_default',
                u'dummy_dict': {
                    u'b': 777
                }
            },
            u'cfg4': {
                u'dummy': u'some_data_default',
                u'dummy_list': [
                    u'item2'
                ],
                u'dummy_dict': {
                    u'b': 999
                }
            },
            u'cfg5': {
                u'dummy': u'some_data_default',
                u'dummy_list': [
                    u'item2'
                ],
                u'dummy_dict': None
            }
        }

    def clean(self):
        try:
            shutil.rmtree(self.cleanup_path)

        except OSError:
            pass

    def get_container(self):
        return self.CFG_ITEM(cfg_fn=self.cfg_fn,
                             cfg_root=self.TEST_CONFIG,
                             key=self.TEST_CONTAINER_KEY)

    def get_container2(self):
        return self.CFG_ITEM(cfg_fn=self.cfg_fn,
                             cfg_root=self.TEST_CONFIG,
                             key=self.TEST_CONTAINER2_KEY)

    def test_instantiation(self):
        self.get_container()

    def test_iter_item(self):
        item = self.get_container()

        params = []

        for param in item:
            params.append(param)
            self.assertIn(param, self.expected_param_dict, u'CfgItem iter failed')

        self.assertEqual(sorted(list(self.expected_param_dict.keys())), sorted(params), u'CfgItem iter failed')

    def test_len_item(self):
        item = self.get_container()

        self.assertEqual(self.expected_len, len(item), u'CfgItem len(item) failed')

    def test_parameters(self):
        item = self.get_container()

        for i in item:
            self.assertEqual(self.expected_param_dict[i],
                             item[i],
                             u'ContainerCfgItem parameters incorrect')

        self.assertEqual(self.expected_param_dict, dict(item), u'ContainerCfgItem parameters do not match')


class TestYAMLContainerCfgItem(TestJSONContainerCfgItem):

    CFG_ITEMS = ExampleItemsYAML
    CFG_ITEM = ExampleContainerYAMLItem

    TEST_CONFIG = TEST_YAML_CONFIG

    FILE_EXT = cfg_params.CONST.yaml

    EXPECTED_STRING = (u"dummy: some_data\n"
                       u"dummy_dict: ordereddict([('a', 1), ('b', 2), ('c', 3)])\n"
                       u"dummy_list: ['item1', 'item2', 'item3']")

    @staticmethod
    def cfg_fn():
        return register_test_yaml_config()

    @staticmethod
    def file_reader(fp):
        yaml = get_default_yaml_instance()
        return yaml.load(fp)


if __name__ == u'__main__':
    unittest.main()
