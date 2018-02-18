# coding=utf-8

from pathlib import Path

import pytest

from edlm.convert import _get_index


def test_get_index():
    ctx = _get_index.Context()
    ctx.source_folder = Path('.').absolute()
    with pytest.raises(FileNotFoundError):
        _get_index.get_index_file(ctx)
    Path('./index.md').mkdir()
    with pytest.raises(TypeError):
        _get_index.get_index_file(ctx)
    Path('./index.md').rmdir()
    Path('./index.md').touch()
    _get_index.get_index_file(ctx)
    assert ctx.index_file == Path('./index.md').absolute()
