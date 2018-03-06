from pathlib import Path

import pytest


here = Path(__file__).parent
data_dir = here / 'data'


@pytest.fixture
def litezip_datadir():
    """Returns the path to the data directory"""
    return data_dir


@pytest.fixture
def litezip_valid_litezip(litezip_datadir):
    """Returns the path to a valid litezip directory"""
    return litezip_datadir / 'litezip'


@pytest.fixture
def litezip_invalid_litezip(litezip_datadir):
    """Returns the path to an invalid litezip directory"""
    return litezip_datadir / 'invalid_litezip'


@pytest.fixture
def litezip_completezip(litezip_datadir):
    """Returns the path to a valid completezip directory"""
    return litezip_datadir / 'completezip'
