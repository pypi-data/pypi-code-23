# encoding: utf-8

import os
from configurationutil import cfg_params, Configuration
from configurationutil.cfg_objects import CfgItems
from configurationutil.cfg_objects.container_cfg_item import ContainerCfgItem
from configurationutil.unittests.test_cfg_objects.inheritable_objects import (ExampleItemsJSONStrict,
                                                                              ExampleItemsYAMLStrict,
                                                                              ExampleInheritableItemJSONStrict,
                                                                              ExampleInheritableItemYAMLStrict)
from fdutil.path_tools import pop_path

# Register Config details (These are expected to be overwritten by an importing app)
cfg_params.APP_NAME = u'PyTestApp'
cfg_params.APP_AUTHOR = u'TEST'
cfg_params.APP_VERSION = u'1.0'

TEST_KEY = u'name'

TEST_JSON_CONFIG = u'test_container_json_cfg_item'
TEST_YAML_CONFIG = u'test_container_yaml_cfg_item'


def register_test_json_config():

    # Retrieve configuration instance
    cfg = Configuration()

    # Register configuration
    cfg.register(config=TEST_JSON_CONFIG,
                 config_type=cfg_params.CONST.json,
                 template=os.path.join(pop_path(__file__), u'..', u'resources',
                                       u'container_cfg_item_template.json'))

    return cfg


def register_test_yaml_config():

    # Retrieve configuration instance
    cfg = Configuration()

    # Register configuration
    cfg.register(config=TEST_YAML_CONFIG,
                 config_type=cfg_params.CONST.yaml,
                 template=os.path.join(pop_path(__file__), u'..', u'resources',
                                       u'container_cfg_item_template.yaml'))

    return cfg


class ExampleContainerJSONItem(ContainerCfgItem):
    ITEMS = ExampleItemsJSONStrict
    STRICT_ITEMS = False


class ExampleContainerYAMLItem(ContainerCfgItem):
    ITEMS = ExampleItemsYAMLStrict
    STRICT_ITEMS = False


class ExampleItemsJSON(CfgItems):

    def __init__(self):
        super(ExampleItemsJSON, self).__init__(cfg_fn=register_test_json_config,
                                               cfg_root=TEST_JSON_CONFIG,
                                               key_name=TEST_KEY,
                                               item_class=ExampleContainerJSONItem)


class ExampleItemsYAML(CfgItems):

    def __init__(self):
        super(ExampleItemsYAML, self).__init__(cfg_fn=register_test_yaml_config,
                                               cfg_root=TEST_YAML_CONFIG,
                                               key_name=TEST_KEY,
                                               item_class=ExampleContainerYAMLItem)
