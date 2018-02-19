# coding=utf-8
"""
Tests path package
"""

from pathlib import Path

import pytest

import elib.path


def test_path():
    path_str = './test'
    path_test = Path('./test')
    assert elib.path.ensure_path(path_str, must_exist=False) == elib.path.ensure_path(path_test, must_exist=False)
    with pytest.raises(FileNotFoundError):
        elib.path.ensure_path(path_str)
    with pytest.raises(FileNotFoundError):
        elib.path.ensure_path(path_test)


def test_dir():
    test = Path('./test')
    assert isinstance(elib.path.ensure_dir(test, must_exist=False), Path)
    test.touch()
    with pytest.raises(TypeError):
        elib.path.ensure_dir(test)
    test.unlink()
    test.mkdir()
    assert isinstance(elib.path.ensure_dir(test), Path)


def test_file():
    test = Path('./test')
    assert isinstance(elib.path.ensure_file(test, must_exist=False), Path)
    test.mkdir()
    with pytest.raises(TypeError):
        elib.path.ensure_file(test)
    test.rmdir()
    test.touch()
    assert isinstance(elib.path.ensure_file(test), Path)


@pytest.mark.parametrize('first', ['some', Path('some')])
@pytest.mark.parametrize('second', ['path', Path('path')])
@pytest.mark.parametrize('third', ['here', Path('here')])
def test_args(first, second, third):
    test = elib.path.ensure_path(first, second, third, must_exist=False)
    assert isinstance(test, Path)
    assert test == Path('some/path/here').absolute()


def test_dir_create():
    path = 'some.dir'
    test = Path(path).absolute()
    assert not test.exists()
    result = elib.path.ensure_dir(path, must_exist=False, create=True)
    assert test.exists()
    assert test == result
