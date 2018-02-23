# coding=utf-8
import pytest


@pytest.mark.parametrize('ext', ['yaml', 'yml'])
def test_yaml_config_file(dummy_config, ext):
    with open(f'test.{ext}', 'w') as stream:
        stream.write('''
debug: "true"
string: some string
integer: 1
''')
    cfg = dummy_config('test')
    assert cfg.debug is True
    assert cfg.string == 'some string'
    assert cfg.integer is 1


@pytest.mark.parametrize('ext', ['yaml', 'yml'])
def test_yaml_list_of_str(dummy_config, ext):
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
    cfg = dummy_config('test')
    assert cfg.some_list == ['caribou', 'gopher', 'moose']


@pytest.mark.parametrize('ext', ['yaml', 'yml'])
def test_yaml_list_of_int(dummy_config, ext):
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
    cfg = dummy_config('test')
    assert cfg.some_list == [0, -4, 3]


@pytest.mark.parametrize('ext', ['yaml', 'yml'])
def test_yaml_namespace(dummy_config, ext):
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
  key: 'caribou'
''')
    cfg = dummy_config('test')
    assert cfg.namespace_key == 'caribou'
