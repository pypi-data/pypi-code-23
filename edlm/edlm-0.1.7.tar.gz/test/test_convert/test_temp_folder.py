# coding=utf-8

import pytest

from edlm.convert._temp_folder import Context, TempDir


def test_temp_dir():
    ctx = Context()
    assert ctx.temp_dir is None
    with TempDir(ctx):
        assert ctx.temp_dir.is_dir()
        assert ctx.temp_dir.exists()
        temp_dir = ctx.temp_dir

    assert ctx.temp_dir is None
    assert not temp_dir.exists()


def test_temp_dir_keep():
    ctx = Context()
    ctx.keep_temp_dir = True
    assert ctx.temp_dir is None
    with TempDir(ctx):
        assert ctx.temp_dir.is_dir()
        assert ctx.temp_dir.exists()
        temp_dir = ctx.temp_dir

    assert ctx.temp_dir == temp_dir
    assert temp_dir.exists()


def test_temp_dir_with_error():
    ctx = Context()
    assert ctx.temp_dir is None
    with pytest.raises(TypeError):
        with TempDir(ctx):
            assert ctx.temp_dir.is_dir()
            assert ctx.temp_dir.exists()
            temp_dir = ctx.temp_dir
            raise TypeError()

    assert ctx.temp_dir == temp_dir
    assert temp_dir.exists()
