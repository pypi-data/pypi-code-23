# coding=utf-8

from pathlib import Path

import pytest

from edlm.convert._context import Context, _Val


@pytest.mark.parametrize(
    'level',
    ['debug', 'info', 'warning', 'error']
)
def test_logger(caplog, level):
    caplog.clear()
    ctx = Context()
    func = getattr(ctx, level)
    assert 'test' not in caplog.text
    func('test')
    assert 'test' in caplog.text


@pytest.mark.parametrize(
    'level',
    ['debug', 'info', 'warning', 'error']
)
def test_logger_with_index_file(caplog, level):
    caplog.clear()
    ctx = Context()
    index_file = Path('index.md').absolute()
    ctx.index_file = index_file
    func = getattr(ctx, level)
    assert 'test' not in caplog.text
    func('test')
    assert 'test' in caplog.text
    assert str(index_file) in caplog.text


def test_no_default():
    class Dummy(Context):
        no_default = _Val(str)

    dummy = Dummy()
    with pytest.raises(KeyError):
        _ = dummy.no_default


def test_wrong_type():
    ctx = Context()
    with pytest.raises(TypeError):
        ctx.title = 1


def test_sub_context():
    ctx = Context()
    sub_context = ctx.get_sub_context()
    assert isinstance(sub_context, Context)
    assert isinstance(sub_context.data, dict)
    for k, v in sub_context.data.items():
        if k in ['settings']:
            continue
        assert ctx.data[k] == v
