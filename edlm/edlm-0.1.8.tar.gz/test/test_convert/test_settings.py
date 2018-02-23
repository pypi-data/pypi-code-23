# coding=utf-8
from pathlib import Path

import pytest

import edlm.convert._get_settings as settings
from edlm.convert import Context, ConvertError, _settings


def _get_dicts():
    source_dict = {
        'source': 'source',
        'shared': 'source',
        'sub': {
            'source': 'source',
            'shared': 'source',
        }
    }
    target_dict = {
        'target': 'target',
        'shared': 'target',
        'sub': {
            'target': 'target',
            'shared': 'target',
        }
    }
    return source_dict, target_dict


def test_update_nested_dict():
    settings_ = _settings.Settings()
    source_dict, target_dict = _get_dicts()
    settings_.update(source_dict)
    settings_.update(target_dict)
    assert settings_.data == {
        'source': 'source',
        'shared': 'target',
        'target': 'target',
        'sub': {
            'source': 'source',
            'shared': 'target',
            'target': 'target',
        }
    }


def test_no_setting_file():
    ctx = Context()
    ctx.source_folder = Path('.').absolute()
    with pytest.raises(ConvertError):
        settings.get_settings(ctx)


def test_single_settings():
    ctx = Context()
    ctx.source_folder = Path('.').absolute()
    settings_ = Path('./settings.yml')
    settings_.write_text('key: value')
    settings.get_settings(ctx)
    assert ctx.settings.data == {'key': 'value'}


def test_empty_settings():
    ctx = Context()
    ctx.source_folder = Path('.').absolute()
    settings_ = Path('./settings.yml')
    settings_.write_text('', encoding='utf8')
    with pytest.raises(ConvertError):
        settings.get_settings(ctx)


def test_nested_settings():
    sub1 = Path('./sub1').absolute()
    sub1.mkdir()
    settings_1 = Path(sub1, 'settings.yml').absolute()
    settings_1.write_text(
        'key1: value1\n'
        'key2: value1\n'
        'key3: value1\n'
        'key4:\n'
        '  key1: value1\n'
        '  key2: value1\n'
        '  key3: value1\n',
        encoding='utf8'
    )
    sub2 = Path(sub1, 'sub2').absolute()
    sub2.mkdir()
    settings_2 = Path(sub2, 'settings.yml').absolute()
    settings_2.write_text(
        'key2: value2\n'
        'key4:\n'
        '  key2: value2\n',
        encoding='utf8'
    )
    sub3 = Path(sub2, 'sub3').absolute()
    sub3.mkdir()
    settings_3 = Path(sub3, 'settings.yml').absolute()
    settings_3.write_text(
        'key3: value3\n'
        'key4:\n'
        '  key3: value3\n',
        encoding='utf8'
    )
    ctx = Context()
    ctx.source_folder = sub3
    settings.get_settings(ctx)
    assert ctx.settings.data == {
        'key1': 'value1',
        'key2': 'value2',
        'key3': 'value3',
        'key4': {
            'key1': 'value1',
            'key2': 'value2',
            'key3': 'value3',
        },
    }


def test_no_default():
    class Dummy(_settings.Settings):
        no_default = _settings._Val(str)

    settings_ = Dummy()
    with pytest.raises(KeyError):
        _ = settings_.no_default


def test_wrong_type():
    settings_ = _settings.Settings()
    with pytest.raises(TypeError):
        settings_.references = 'test'
