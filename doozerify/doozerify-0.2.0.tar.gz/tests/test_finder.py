"""Tests for doozerify.Finder."""

import sys

import pytest

import doozerify


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


def test_module_not_found(meta_path):
    """Test that modulenotfounderror is raised."""
    with pytest.raises(ModuleNotFoundError):
        import henson  # NOQA: F401
