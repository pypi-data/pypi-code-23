"""Test path functions."""

import os

from utilp.func import (  # noqa: F401
    is_pathname_valid,
    is_path_creatable,
    path_exists_or_creatable,
    is_path_sibling_creatable,
    path_exists_or_creatable_portable,
)


TEST_FPATH = os.path.expanduser('~/temp.txt')


def test_path_functions():
    assert is_pathname_valid(TEST_FPATH)
    assert is_path_creatable(TEST_FPATH)
    assert path_exists_or_creatable(TEST_FPATH)
    assert is_path_sibling_creatable(TEST_FPATH)
    assert path_exists_or_creatable_portable(TEST_FPATH)
