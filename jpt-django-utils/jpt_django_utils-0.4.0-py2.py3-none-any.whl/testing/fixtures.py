"""Pytest fixtures."""
import pytest

from .client import JSONClient


@pytest.fixture
def json_client():
    """JSONClient pytest fixture."""
    return JSONClient()
