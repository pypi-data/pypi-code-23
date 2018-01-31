"""Tests for api utils"""
import jwt
import pytest

from open_discussions_api.utils import get_token


def test_get_token():
    """Test that get_token encodes a token decodable by the secret"""
    token = get_token(
        'secret',
        'username',
        ['test_role'],
        expires_delta=100,
        extra_payload=dict(auth_url='auth', session_url='session')
    )
    decoded = jwt.decode(token, 'secret', algorithms=['HS256'])
    assert decoded['username'] == 'username'
    assert decoded['roles'] == ['test_role']
    assert decoded['exp'] == decoded['orig_iat'] + 100
    assert decoded['auth_url'] == 'auth'
    assert decoded['session_url'] == 'session'


def test_get_token_error():
    """Test that get_token raises an ArgumentError if a bad extra_payload arg is passed"""

    with pytest.raises(AttributeError):
        get_token(
            'secret',
            'username',
            ['test_role'],
            expires_delta=100,
            extra_payload=dict(auth_url='auth', username='username')  # username is a default item in the payload
        )
