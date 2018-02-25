"""Tests for doozerify.FallbackFinder."""

import sys

import pytest

import doozerify


def test_fallback_finder_doozer_extension_only(
        meta_path_fallback,
        doozer_extension_import,
):
    """Test that the Doozer-based extension is imported."""
    import doozer_extension
    assert doozer_extension.__name__ == 'doozer-extension'


def test_fallback_finder_doozer_only(meta_path_fallback, doozer_import):
    """Test that doozer is imported."""
    import doozer
    assert doozer.__name__ == 'doozer'


def test_fallback_finder_henson_extension_only(
        meta_path_fallback,
        henson_extension_import,
):
    """Test that the Henson-based extension is imported."""
    import doozer_extension
    assert doozer_extension.__name__ == 'henson-extension'


def test_fallback_finder_henson_only(meta_path_fallback, henson_import):
    """Test that henson is imported."""
    import doozer
    assert doozer.__name__ == 'henson'


def test_fallback_finder_doozer_extension_over_henson(
        meta_path_fallback,
        doozer_extension_import,
):
    """Test that the Doozer-based extension is imported."""
    import doozer_extension
    assert doozer_extension.__name__ == 'doozer-extension'


def test_fallback_finder_picks_doozer_over_henson(
        meta_path_fallback,
        doozer_import,
        henson_import,
):
    """Test that doozer is imported."""
    import doozer
    assert doozer.__name__ == 'doozer'


def test_install_fallback(meta_path_fallback):
    """Test that fallback install adds the finder to the meta path."""
    # install is called by the meta_path fixture.
    assert any(f is doozerify.FallbackFinder for f in sys.meta_path)


def test_module_not_found_with_fallback(meta_path_fallback):
    """Test that ModuleNotFoundError is raised."""
    with pytest.raises(ModuleNotFoundError):
        import doozer  # NOQA: F401
