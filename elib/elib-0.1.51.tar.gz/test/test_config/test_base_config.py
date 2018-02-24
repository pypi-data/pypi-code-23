# coding=utf-8
from pathlib import Path

import everett
import pytest

from elib.config import ConfigProp


class WrongBaseClass:
    """
    Does not inherit BaseConfig
    """
    string = ConfigProp(str, '')


def test_create_config(dummy_config):
    cfg = dummy_config('test')
    assert cfg.debug is False
    assert not cfg.string
    assert cfg.integer is 0


@pytest.mark.parametrize('key', ['debug', 'DEBUG'])
def test_default_dict(dummy_config, key):
    cfg = dummy_config(
        'test', {key: 'true', 'string': 'some string', 'integer': 1})
    assert cfg.debug is True
    assert cfg.string == 'some string'
    assert cfg.integer is 1


def test_no_default(dummy_config):
    cfg = dummy_config('test')
    with pytest.raises(everett.ConfigurationMissingError):
        assert cfg.no_default == 'value'


def test_wrong_base_class():
    test = WrongBaseClass()
    with pytest.raises(TypeError):
        print(test.string)


def test_calling_from_instance(dummy_config):
    assert isinstance(dummy_config().integer, ConfigProp)


def test_empty_config_file(dummy_config):
    Path('./test.yml').touch()
    cfg = dummy_config('test')
    assert cfg.debug is False
