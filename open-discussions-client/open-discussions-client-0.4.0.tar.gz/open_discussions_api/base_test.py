"""Tests for base API class"""

from open_discussions_api.base import BaseApi


def test_get_url():
    """Test that get_url returns absolute url"""
    base = BaseApi(None, 'http://example.com', 'v0')
    assert base.get_url('/my/api') == 'http://example.com/api/v0/my/api'
    assert base.get_url('my/api') == 'http://example.com/api/v0/my/api'
