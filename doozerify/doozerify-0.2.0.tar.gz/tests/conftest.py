"""Test configuration."""

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


@pytest.fixture
def meta_path_fallback(monkeypatch):
    """Install the fallback finder."""
    monkeypatch.setattr(sys, 'meta_path', sys.meta_path.copy())
    doozerify.install_fallback()
