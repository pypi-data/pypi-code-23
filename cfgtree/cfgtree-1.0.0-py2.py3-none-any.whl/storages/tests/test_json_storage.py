# coding: utf-8

# Standard Libraries
import os
from pathlib import Path

# Third Party Libraries
import pytest

# Cfgtree modules
from cfgtree import ConfigBaseModel
from cfgtree.cmdline_parsers.dummy import DummyCmdlineParser
from cfgtree.storages.json import JsonFileConfigStorage
from cfgtree.types import BoolCfg
from cfgtree.types import ConfigFileCfg
from cfgtree.types import ConfigVersionCfg
from cfgtree.types import FloatCfg
from cfgtree.types import IntCfg
from cfgtree.types import ListOfStringCfg
from cfgtree.types import StringCfg

# flake8: noqa=E122
# pylint: disable=redefined-outer-name, unused-argument


@pytest.fixture
def cfg():
    class MyAppConfig(ConfigBaseModel):

        environ_var_prefix = "MYAPP_"

        storage = JsonFileConfigStorage(
            environ_var="MYAPP_COMMON_CONFIG_FILE",
            long_param="--config",
            short_param="-c",
            default_filename="config.json",
        )

        cmd_line_parser = DummyCmdlineParser()

        model = {
            "configfile": ConfigFileCfg(long_param="--configfile", summary="Config file"),
            "version": ConfigVersionCfg(),
            "group1": {
                "string_opt":
                    StringCfg(
                        short_param='-s', long_param="--string-opt", summary='Help msg string'),
                "int_opt":
                    IntCfg(short_param='-i', long_param="--int-opt", summary='Help msg int'),
                "float_opt":
                    FloatCfg(short_param='-f', long_param="--float-opt", summary='Help msg float'),
                "bool_opt":
                    BoolCfg(short_param='-b', long_param="--bool-opt", summary='Help msg bool'),
                "list_opt":
                    ListOfStringCfg(
                        short_param='-l', long_param="--list-opt", summary='Help msg lst'),
                "dict_opt": {
                    "key1": StringCfg(summary='Help msg string'),
                    "key2": StringCfg(summary='Help msg string'),
                }
            }
        }

    model = MyAppConfig()
    yield model


@pytest.fixture
def environ():
    old_env = os.environ.copy()
    yield os.environ
    os.environ = old_env


def test_load_config_model(cfg, environ):
    config = Path(__file__).parent / "vectors" / "json" / "config.json"
    environ['MYAPP_COMMON_CONFIG_FILE'] = str(config)
    cfg.find_configuration_values()
    assert cfg.get_cfg_value("version") == 1
    assert cfg.get_cfg_value("group1.string_opt") == 'a string'
    assert cfg.get_cfg_value("group1.int_opt") == 123
    assert cfg.get_cfg_value("group1.float_opt") == 2.0
    assert cfg.get_cfg_value("group1.bool_opt") is True
    assert cfg.get_cfg_value("group1.list_opt") == ['a', 'b', 'c']
    assert cfg.get_cfg_value("group1.dict_opt.key1") == "val1"
