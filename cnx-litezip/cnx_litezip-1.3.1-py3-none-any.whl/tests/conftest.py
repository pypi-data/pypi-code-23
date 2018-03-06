import pytest


@pytest.fixture
def datadir(litezip_datadir):
    """Returns the path to the data directory"""
    return litezip_datadir
