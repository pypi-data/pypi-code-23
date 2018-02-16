"""Test the (minimal) version file."""

from rest_easy.version import __version__, __version_info__


def test_version_info():
    assert isinstance(__version_info__, tuple)
    assert len(__version_info__) == 3


def test_version():
    assert isinstance(__version__, str)
    split = __version__.split('.')
    assert len(split) == 3
    v_info = tuple(int(i) for i in split)
    assert v_info == __version_info__
