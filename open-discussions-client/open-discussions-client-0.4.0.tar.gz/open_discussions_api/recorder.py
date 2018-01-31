"""Add context manager to make recording open-discussion requests simpler"""
from contextlib import contextmanager
from unittest.mock import patch

from betamax import Betamax
import requests

from open_discussions_api.client import OpenDiscussionsApi
from open_discussions_api.betamax_config import setup_betamax


@contextmanager
def record(name, username, roles=None):
    """
    Record a cassette of some reddit communication.

    Usage:
        with record('cassette_name', 'username', roles=[ROLE_STAFF]) as api:
            api.users.list()

    Args:
        name (str): The name of the new cassette
        username (str): username to authenticate with
        roles (list(str)): roles the user has
    """
    setup_betamax()
    session = requests.Session()
    session.verify = False

    with patch('open_discussions_api.client.OpenDiscussionsApi._get_session', return_value=session):
        with Betamax(session).use_cassette(name):
            api = OpenDiscussionsApi(
                'terribly_unsafe_default_jwt_secret_key',
                'http://localhost:8063/',
                username,
                roles=roles or []
            )
            yield api
