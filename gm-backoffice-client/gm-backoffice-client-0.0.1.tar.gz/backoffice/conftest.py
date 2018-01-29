import pytest

from .client import BackofficeClient


@pytest.fixture
def backoffice():
    return BackofficeClient(
        url='http://testhost',
        token='tsttkn',
    )
