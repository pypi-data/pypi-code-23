# coding=utf-8
"""
Config test
"""
from pathlib import Path

import everett
import pytest

from elib.config import BaseConfig
from elib.config.property import ConfigProp


class WrongBaseClass:
    """
    Does not inherit BaseConfig
    """
    string = ConfigProp(str, '')


class DummyConfig(BaseConfig):
    """Dummy test class for Config"""

    debug = ConfigProp(bool, 'false')
    string = ConfigProp(str, '')
    integer = ConfigProp(int, '0')
    some_list = ConfigProp(list, '[]')
    namespace_key = ConfigProp(str, namespace='namespace')
    no_default = ConfigProp(str)


def test_create_config():
    cfg = DummyConfig('test')
    assert cfg.debug is False
    assert not cfg.string
    assert cfg.integer is 0


def test_ini_config_file():
    with open('test.ini', 'w') as stream:
        stream.write('''
[main]
debug=true
string=some string
integer=1
''')
    cfg = DummyConfig('test')
    assert cfg.debug is True
    assert cfg.string == 'some string'
    assert cfg.integer is 1


@pytest.mark.parametrize('ext', ['yaml', 'yml'])
def test_yaml_config_file(ext):
    with open(f'test.{ext}', 'w') as stream:
        stream.write('''
debug: "true"
string: some string
integer: 1
''')
    cfg = DummyConfig('test')
    assert cfg.debug is True
    assert cfg.string == 'some string'
    assert cfg.integer is 1


@pytest.mark.parametrize('key', ['debug', 'DEBUG'])
def test_default_dict(key):
    cfg = DummyConfig(
        'test', {key: 'true', 'string': 'some string', 'integer': 1})
    assert cfg.debug is True
    assert cfg.string == 'some string'
    assert cfg.integer is 1


@pytest.mark.parametrize('ext', ['yaml', 'yml'])
def test_yaml_list_of_str(ext):
    with open(f'test.{ext}', 'w') as stream:
        stream.write('''
debug: "true"
string: some string
integer: 1
some_list:
  - caribou
  - gopher
  - moose
''')
    cfg = DummyConfig('test')
    assert cfg.some_list == ['caribou', 'gopher', 'moose']


@pytest.mark.parametrize('ext', ['yaml', 'yml'])
def test_yaml_list_of_int(ext):
    with open(f'test.{ext}', 'w') as stream:
        stream.write('''
debug: "true"
string: some string
integer: 1
some_list:
  - 0
  - -4
  - 3
''')
    cfg = DummyConfig('test')
    assert cfg.some_list == [0, -4, 3]


@pytest.mark.parametrize('ext', ['yaml', 'yml'])
def test_yaml_namespace(ext):
    with open(f'test.{ext}', 'w') as stream:
        stream.write('''
debug: "true"
string: "some string"
integer: 1
some_list:
  - caribou
  - gopher
  - moose
namespace:
  namespace_key: 'caribou'
''')
    cfg = DummyConfig('test')
    assert cfg.namespace_key == 'caribou'


def test_no_default():
    cfg = DummyConfig('test')
    with pytest.raises(everett.ConfigurationMissingError):
        assert cfg.no_default == 'value'


def test_wrong_base_class():
    test = WrongBaseClass()
    with pytest.raises(TypeError):
        print(test.string)


def test_calling_from_instance():
    assert isinstance(DummyConfig.integer, ConfigProp)


def test_empty_config_file():
    Path('./test.yml').touch()
    cfg = DummyConfig('test')
    assert cfg.debug is False
