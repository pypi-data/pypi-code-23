# coding: utf-8

# Standard Libraries
from pathlib import Path

# Third Party Libraries
import pytest

# Cfgtree modules
from cfgtree import ConfigBaseModel
from cfgtree.cmdline_parsers.dummy import DummyCmdlineParser
from cfgtree.storages.json import JsonFileConfigStorage
from cfgtree.storages.tests._common import environ  # pylint: disable=unused-import
from cfgtree.storages.tests._common import model_test_json

# flake8: noqa=E122
# pylint: disable=redefined-outer-name, unused-argument


@pytest.fixture
def cfg(environ):
    config = Path(__file__).parent / "vectors" / "json" / "config.json"
    environ['MYAPP_COMMON_CONFIG_FILE'] = str(config)

    class MyAppConfig(ConfigBaseModel):

        environ_var_prefix = "MYAPP_"

        storage = JsonFileConfigStorage(
            environ_var="MYAPP_COMMON_CONFIG_FILE",
            long_param="--config",
            short_param="-c",
            default_filename="config.json",
        )

        cmd_line_parser = DummyCmdlineParser()

        model = model_test_json(config)

    model = MyAppConfig()
    yield model


def test_load_config_model(cfg, environ):
    cfg.find_configuration_values()
    assert cfg.get_cfg_value("version") == 1
    assert cfg.get_cfg_value("group1.string_opt") == 'a string'
    assert cfg.get_cfg_value("group1.int_opt") == 123
    assert cfg.get_cfg_value("group1.float_opt") == 2.0
    assert cfg.get_cfg_value("group1.bool_opt") is True
    assert cfg.get_cfg_value("group1.list_opt") == ['a', 'b', 'c']
    assert cfg.get_cfg_value("group1.dict_opt.key1") == "val1"
