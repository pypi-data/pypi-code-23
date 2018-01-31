"""Tests for client API class"""
import pytest

from open_discussions_api.client import OpenDiscussionsApi
from open_discussions_api.users.client import UsersApi


def test_client_invalid_secret():
    """Test that the API errors if not passed secret"""
    with pytest.raises(AttributeError) as err:
        OpenDiscussionsApi('', 'http://example.com', 'username')
    assert str(err.value) == "secret is required"


def test_client_invalid_base_url():
    """Test that the API errors if not passed base_url"""
    with pytest.raises(AttributeError) as err:
        OpenDiscussionsApi('secret', '', 'username')
    assert str(err.value) == "base_url is required"


def test_users():
    """Test that users api gets configured correctly"""
    client = OpenDiscussionsApi('secret', 'http://example.com', 'username', version='v1')
    assert isinstance(client.users, UsersApi)
    assert client.users.session.headers['Authorization'].startswith('Bearer ')
    assert client.users.base_url == 'http://example.com'
    assert client.users.version == 'v1'
