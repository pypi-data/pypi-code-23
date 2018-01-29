# coding: utf-8

# Standard Libraries
from pathlib import Path

# Third Party Libraries
import pytest

# Cfgtree modules
from cfgtree.models.anyconfig import AnyConfigModel
from cfgtree.storages.tests._common import environ  # pylint: disable=unused-import
from cfgtree.storages.tests._common import model_test_json
from cfgtree.storages.tests._common import run_within_cli

# flake8: noqa=E122
# pylint: disable=redefined-outer-name, unused-argument


@pytest.fixture
def cfg(environ):
    config = Path(__file__).parent / "vectors" / "json" / "config.json"
    environ['MYAPP_COMMON_CONFIG_FILE'] = str(config)
    yield AnyConfigModel(model=model_test_json(config))


def test_load_config_model(cfg):
    cfg.find_configuration_values()
    assert cfg.get_cfg_value("version") == 1
    assert cfg.get_cfg_value("group1.string_opt") == 'a string'
    assert cfg.get_cfg_value("group1.dict_opt.key1") == "val1"


def test_cli_parsing():
    argv = ([
        "app", "--config-file",
        (Path(__file__).parent / "vectors" / "json" / "config.json").as_posix()
    ])
    run_within_cli(argv)
