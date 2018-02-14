# coding=utf-8
"""
Tests TTS package
"""

from pathlib import Path

import pytest
from elib.tts import text_to_speech

# from httmock import all_requests, response
# from requests import PreparedRequest


#
# @all_requests
# def correct_response(url, request: PreparedRequest):
#     if request.url == 'https://translate.google.com/':
#         return response(
#             200,
#             content={'text': r";MAX_ALTERNATIVES_ROUNDTRIP_RESULTS=1;"
#                              r"TKK=eval('((function(){var a\x3d1869649412;var b\x3d1066560713;"
#                              r"return 420586+\x27.\x27+(a+b)})())');WEB_TRANSLATION_PATH="})
#     print(url, request)
#     return response(200, content={'url': 'content'})
#
#
# @all_requests
# def bad_response(*_):
#     return response(500, content={'reason': 'reason'})


def test_tts_correct():
    file = Path('test.file')
    assert not file.exists()
    text_to_speech('some text', file)
    assert (file.exists())
    with pytest.raises(FileExistsError):
        text_to_speech('some text', file)
