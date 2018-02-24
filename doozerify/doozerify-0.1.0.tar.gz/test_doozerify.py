"""Tests for doozerify."""

import sys

import pytest

import doozerify


@pytest.fixture
def site_packages(monkeypatch, tmpdir):
    """Add a temporary directory to PYTHONPATH."""
    tmpdir = tmpdir.mkdir('site-packages')
    monkeypatch.syspath_prepend(str(tmpdir))

    # Anything imported from here will be imported into sys.modules so
    # that needs to be cleaned up as well.
    monkeypatch.setattr(sys, 'modules', sys.modules.copy())

    return tmpdir


@pytest.fixture
def doozer_import(site_packages):
    """Create a package named doozer."""
    doozer = site_packages.join('doozer.py')
    doozer.write('__name__ = "doozer"')


@pytest.fixture
def doozer_extension_import(site_packages):
    """Create a Doozer-based extension."""
    doozer_extension = site_packages.join('doozer_extension.py')
    doozer_extension.write('__name__ = "doozer-extension"')


@pytest.fixture
def henson_import(site_packages):
    """Create a package named henson."""
    henson = site_packages.join('henson.py')
    henson.write('__name__ = "henson"')


@pytest.fixture
def henson_extension_import(site_packages):
    """Create a Henson-based extension."""
    henson_extension = site_packages.join('henson_extension.py')
    henson_extension.write('__name__ = "henson-extension"')


@pytest.fixture
def meta_path(monkeypatch):
    """Install the doozerify finder."""
    monkeypatch.setattr(sys, 'meta_path', sys.meta_path.copy())
    doozerify.install()


def test_finder_doozer_extension_only(meta_path, doozer_extension_import):
    """Test that the Doozer-based extension is imported."""
    import henson_extension
    assert henson_extension.__name__ == 'doozer-extension'


def test_finder_doozer_only(meta_path, doozer_import):
    """Test that doozer is imported."""
    import henson
    assert henson.__name__ == 'doozer'


def test_finder_henson_extension_only(meta_path, henson_extension_import):
    """Test that the Henson-based extension is imported."""
    import henson_extension
    assert henson_extension.__name__ == 'henson-extension'


def test_finder_henson_only(meta_path, henson_import):
    """Test that henson is imported."""
    import henson
    assert henson.__name__ == 'henson'


def test_finder_picks_doozer_extension_over_henson(
        meta_path,
        doozer_extension_import,
        henson_extension_import,
):
    """Test that the Doozer-based extension is imported."""
    import henson_extension
    assert henson_extension.__name__ == 'doozer-extension'


def test_finder_picks_doozer_over_henson(
        meta_path,
        doozer_import,
        henson_import,
):
    """Test that doozer is imported."""
    import henson
    assert henson.__name__ == 'doozer'


def test_install(meta_path):
    """Test that install adds the finder to the meta path."""
    # install is called by the meta_path fixture.
    assert any(f is doozerify.Finder for f in sys.meta_path)
