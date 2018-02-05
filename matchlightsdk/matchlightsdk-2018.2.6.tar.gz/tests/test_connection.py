"""Unit tests Matchlight SDK connection objects."""
import pytest

import matchlight


def test_invalid_connection():
    """Verify SDK error thrown when initializing an invalid connection."""
    with pytest.raises(matchlight.SDKError):
        matchlight.Matchlight(access_key=None, secret_key=None)


def test_connection_with_environment(monkeypatch, access_key, secret_key):
    """Verify the connection uses access and secret keys from environment."""
    monkeypatch.setenv('MATCHLIGHT_ACCESS_KEY', access_key)
    monkeypatch.setenv('MATCHLIGHT_SECRET_KEY', secret_key)
    ml = matchlight.Matchlight()
    assert ml.conn.access_key == access_key
    assert ml.conn.secret_key == secret_key
