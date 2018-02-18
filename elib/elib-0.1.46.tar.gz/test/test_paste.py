# coding=utf-8
"""
Tests paste package
"""

import pytest
from httmock import HTTMock, all_requests, response

from elib.paste import PasteContent, PasteError, create_new_paste


@all_requests
def correct_response(*_):
    """Returns a correct response"""
    return response(200, content={'url': 'content'})


@all_requests
def bad_response(*_):
    """Returns  a bad response"""
    return response(500, content={'reason': 'reason'})


def test_pastebin_correct():
    with HTTMock(correct_response):
        content = PasteContent('test.lua', """print('caribou')""")
        resp = create_new_paste('test', [content])
        assert resp == 'content'


def test_pastebin_bad():
    with HTTMock(bad_response):
        content = PasteContent('test.lua', """print('caribou')""")
        with pytest.raises(PasteError):
            create_new_paste('test', [content])
