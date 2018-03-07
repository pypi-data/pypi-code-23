# encoding: utf-8

import os
from configurationutil import cfg_params, Configuration
from configurationutil.cfg_objects import cfg_items
from configurationutil.cfg_objects.inheritable_cfg_item import InheritableCfgItem
from fdutil.path_tools import pop_path

# Register Config details (These are expected to be overwritten by an importing app)
cfg_params.APP_NAME = u'PyTestApp'
cfg_params.APP_AUTHOR = u'TEST'
cfg_params.APP_VERSION = u'1.0'

TEST_KEY = u'name'
TEST_DEFAULT_PARAMS = {
    u'dummy': u'',
    u'dummy_list': [],
    u'dummy_dict': {},
    u'dummy_extra': 123
}

TEST_JSON_CONFIG = u'test_inheritable_json_cfg_item'
TEST_JSON_CONFIG_STRICT = u'test_inheritable_json_cfg_item_strict'

TEST_YAML_CONFIG = u'test_inheritable_yaml_cfg_item'
TEST_YAML_CONFIG_STRICT = u'test_inheritable_yaml_cfg_item_strict'


def register_test_json_config():

    # Retrieve configuration instance
    cfg = Configuration()

    # Register configuration
    cfg.register(config=TEST_JSON_CONFIG,
                 config_type=cfg_params.CONST.json,
                 template=os.path.join(pop_path(__file__), u'..', u'resources',
                                       u'inheritable_cfg_item_template.json'))

    return cfg


def register_test_json_config_strict():

    # Retrieve configuration instance
    cfg = Configuration()

    # Register configuration
    cfg.register(config=TEST_JSON_CONFIG_STRICT,
                 config_type=cfg_params.CONST.json,
                 template=os.path.join(pop_path(__file__), u'..', u'resources',
                                       u'inheritable_cfg_item_template.json'))

    return cfg


def register_test_json_items_config():

    # Retrieve configuration instance
    cfg = Configuration()

    # Register configuration
    cfg.register(config=TEST_JSON_CONFIG,
                 config_type=cfg_params.CONST.json,
                 template=os.path.join(pop_path(__file__), u'..', u'resources',
                                       u'inheritable_cfg_items_template.json'))

    return cfg


def register_test_json_items_config_strict():

    # Retrieve configuration instance
    cfg = Configuration()

    # Register configuration
    cfg.register(config=TEST_JSON_CONFIG_STRICT,
                 config_type=cfg_params.CONST.json,
                 template=os.path.join(pop_path(__file__), u'..', u'resources',
                                       u'inheritable_cfg_items_template.json'))

    return cfg


def register_test_yaml_config():

    # Retrieve configuration instance
    cfg = Configuration()

    # Register configuration
    cfg.register(config=TEST_YAML_CONFIG,
                 config_type=cfg_params.CONST.yaml,
                 template=os.path.join(pop_path(__file__), u'..', u'resources',
                                       u'inheritable_cfg_item_template.yaml'))

    return cfg


def register_test_yaml_config_strict():

    # Retrieve configuration instance
    cfg = Configuration()

    # Register configuration
    cfg.register(config=TEST_YAML_CONFIG_STRICT,
                 config_type=cfg_params.CONST.yaml,
                 template=os.path.join(pop_path(__file__), u'..', u'resources',
                                       u'inheritable_cfg_item_template.yaml'))

    return cfg


def register_test_yaml_items_config():

    # Retrieve configuration instance
    cfg = Configuration()

    # Register configuration
    cfg.register(config=TEST_YAML_CONFIG,
                 config_type=cfg_params.CONST.yaml,
                 template=os.path.join(pop_path(__file__), u'..', u'resources',
                                       u'inheritable_cfg_items_template.yaml'))

    return cfg


def register_test_yaml_items_config_strict():

    # Retrieve configuration instance
    cfg = Configuration()

    # Register configuration
    cfg.register(config=TEST_YAML_CONFIG_STRICT,
                 config_type=cfg_params.CONST.yaml,
                 template=os.path.join(pop_path(__file__), u'..', u'resources',
                                       u'inheritable_cfg_items_template.yaml'))

    return cfg


# Strict=True example
class ExampleItemsJSONStrict(cfg_items.CfgItems):

    def __init__(self):
        super(ExampleItemsJSONStrict, self).__init__(cfg_fn=register_test_json_items_config_strict,
                                                     cfg_root=TEST_JSON_CONFIG_STRICT,
                                                     key_name=TEST_KEY,
                                                     item_class=ExampleInheritableItemJSONStrict)


class ExampleInheritableItemJSONStrict(InheritableCfgItem):
    DEFAULT_PARAMS = TEST_DEFAULT_PARAMS


class ExampleItemsYAMLStrict(cfg_items.CfgItems):

    def __init__(self):
        super(ExampleItemsYAMLStrict, self).__init__(cfg_fn=register_test_yaml_items_config_strict,
                                                     cfg_root=TEST_YAML_CONFIG_STRICT,
                                                     key_name=TEST_KEY,
                                                     item_class=ExampleInheritableItemYAMLStrict)


class ExampleInheritableItemYAMLStrict(InheritableCfgItem):
    DEFAULT_PARAMS = TEST_DEFAULT_PARAMS


# Strict=True Recursive=True
class ExampleItemsJSONRecursive(cfg_items.CfgItems):

    def __init__(self):
        super(ExampleItemsJSONRecursive, self).__init__(cfg_fn=register_test_json_items_config_strict,
                                                        cfg_root=TEST_JSON_CONFIG_STRICT,
                                                        key_name=TEST_KEY,
                                                        item_class=ExampleInheritableItemJSONRecursive)


class ExampleInheritableItemJSONRecursive(InheritableCfgItem):
    DEFAULT_PARAMS = TEST_DEFAULT_PARAMS
    INHERIT_RECURSIVELY = True


class ExampleItemsYAMLRecursive(cfg_items.CfgItems):

    def __init__(self):
        super(ExampleItemsYAMLRecursive, self).__init__(cfg_fn=register_test_yaml_items_config_strict,
                                                        cfg_root=TEST_YAML_CONFIG_STRICT,
                                                        key_name=TEST_KEY,
                                                        item_class=ExampleInheritableItemYAMLRecursive)


class ExampleInheritableItemYAMLRecursive(InheritableCfgItem):
    DEFAULT_PARAMS = TEST_DEFAULT_PARAMS
    INHERIT_RECURSIVELY = True


# Strict=False example
class ExampleItemsJSON(cfg_items.CfgItems):

    def __init__(self):
        super(ExampleItemsJSON, self).__init__(cfg_fn=register_test_json_items_config,
                                               cfg_root=TEST_JSON_CONFIG,
                                               key_name=TEST_KEY,
                                               item_class=ExampleInheritableJSONItem)


class ExampleInheritableJSONItem(InheritableCfgItem):
    STRICT = False
    DEFAULT_PARAMS = TEST_DEFAULT_PARAMS


class ExampleItemsYAML(cfg_items.CfgItems):

    def __init__(self):
        super(ExampleItemsYAML, self).__init__(cfg_fn=register_test_yaml_items_config,
                                               cfg_root=TEST_YAML_CONFIG,
                                               key_name=TEST_KEY,
                                               item_class=ExampleInheritableYAMLItem)


class ExampleInheritableYAMLItem(InheritableCfgItem):
    STRICT = False
    DEFAULT_PARAMS = TEST_DEFAULT_PARAMS
