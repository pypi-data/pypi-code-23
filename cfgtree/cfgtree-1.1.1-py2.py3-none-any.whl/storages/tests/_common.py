# coding: utf-8

# Standard Libraries
import logging
import logging.config
import os
import sys

# Third Party Libraries
import pytest

# Cfgtree modules
from cfgtree.models.anyconfig import AnyConfigCliModel
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
def environ():
    old_env = os.environ.copy()
    yield os.environ
    os.environ = old_env


def model_test_json(config=None):
    # yapf: disable
    return {
        "configfile": ConfigFileCfg(
            default_filename=config,
            long_param="--config-file",
            summary="Config file"),
        "version": ConfigVersionCfg(),
        "group1": {
            "string_opt": StringCfg(
                short_param='-s',
                long_param="--string-opt",
                summary='Help msg string'),
            "int_opt": IntCfg(
                short_param='-i',
                long_param="--int-opt",
                summary='Help msg int'),
            "float_opt": FloatCfg(
                short_param='-f',
                long_param="--float-opt",
                summary='Help msg float'),
            "bool_opt": BoolCfg(
                short_param='-b',
                long_param="--bool-opt",
                summary='Help msg bool'),
            "list_opt": ListOfStringCfg(
                short_param='-l',
                long_param="--list-opt",
                summary='Help msg lst'),
            "dict_opt": {
                "key1": StringCfg(summary='Help msg string'),
                "key2": StringCfg(summary='Help msg string'),
            }
        }
    }


def run_within_cli(argv=None):
    """
    Run with:

        pipenv run python3 ./cfgtree/storages/tests/_common.py \
                           --config-file cfgtree/storages/tests/vectors/json/config.json
    """
    if argv is None:
        argv = sys.argv
    logging.basicConfig(stream=sys.stdout,
                        level=logging.DEBUG, format="%(message)s")
    cfg = AnyConfigCliModel(model=model_test_json())
    cfg.find_configuration_values(argv=argv)


if __name__ == '__main__':
    run_within_cli()
