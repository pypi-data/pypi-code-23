"""Pytest fixtures"""
# pylint: disable=unused-argument, redefined-outer-name
import pytest

from open_discussions_api.betamax_config import setup_betamax
from open_discussions_api.client import OpenDiscussionsApi
from open_discussions_api.constants import ROLE_STAFF


@pytest.fixture
def configure_betamax():
    """Configure betamax"""
    setup_betamax()


@pytest.fixture
def use_betamax(mocker, configure_betamax, betamax_recorder):
    """Attach the betamax session to the Api client"""
    mocker.patch('open_discussions_api.client.OpenDiscussionsApi._get_session', return_value=betamax_recorder.session)
    return betamax_recorder


@pytest.fixture
def api_client(use_betamax):
    """API client"""
    return OpenDiscussionsApi('secret', 'http://localhost:8063/', 'mitodl', roles=[ROLE_STAFF])
