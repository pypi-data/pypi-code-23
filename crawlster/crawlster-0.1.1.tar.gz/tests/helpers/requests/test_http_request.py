import pytest

from crawlster.helpers.http.request import (
    HttpRequest, GetRequest, PostRequest, XhrRequest, JsonRequest)


def test_request_invalid_method():
    with pytest.raises(ValueError):
        HttpRequest(method='invalid', url="http://example.com")


def test_request_invalid_url():
    with pytest.raises(ValueError):
        HttpRequest('invalid_url')


# noinspection PyTypeChecker
def test_request_invalid_headers():
    with pytest.raises(TypeError):
        HttpRequest('http://localhost', headers='invalid type')


@pytest.mark.parametrize('obj_type, init_args, expected_attrs', [
    (GetRequest, ('http://localhost',), {'method': 'GET'}),
    (PostRequest, ('http://localhost',), {'method': 'POST'}),
    (XhrRequest, ('http://localhost',),
     {'method': 'GET', 'headers': {'X-Requested-With': 'XMLHttpRequest'}}),
    (JsonRequest, ('http://localhost', 'POST', {'hello': 'world'}),
     {
         'content_type': 'application/json',
         'data': '{"hello":"world"}'
     })
])
def test_request_initialisation(obj_type, init_args, expected_attrs):
    instance = obj_type(*init_args)
    for k, v in expected_attrs.items():
        assert getattr(instance, k) == v
