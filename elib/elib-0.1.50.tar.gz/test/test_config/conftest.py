# coding=utf-8

import pytest

from elib.config import BaseConfig, ConfigProp


class DummyConfig(BaseConfig):
    """Dummy test class for Config"""

    debug = ConfigProp(bool, 'false')
    string = ConfigProp(str, '')
    integer = ConfigProp(int, '0')
    some_list = ConfigProp(list, '[]')
    namespace_key = ConfigProp(str, namespace='namespace')
    no_default = ConfigProp(str)


@pytest.fixture()
def dummy_config():
    def make_dummy_config(*args, **kwargs):
        if args or kwargs:
            return DummyConfig(*args, **kwargs)

        return DummyConfig
    yield make_dummy_config
