import pytest

from crawlster.helpers.http.request import HttpRequest
from crawlster.helpers.http.response import HttpResponse


@pytest.fixture
def http_request():
    return HttpRequest('http://localhost')


CASE_1 = 200, {'Server': 'test/1.0'}, b'<p>This is nice</p>', {
    'status_code': 200, 'body_str': '<p>This is nice</p>',
    'body_bytes': b'<p>This is nice</p>', 'server': 'test/1.0'
}

CASE_2 = 200, {'Content-Type': 'application/xml'}, b'<test>ok</test>', {
    'status_code': 200, 'body_str': '<test>ok</test>',
    'body_bytes': b'<test>ok</test>', 'content_type': 'application/xml'
}


@pytest.mark.parametrize('status_code, headers, body, expected', [
    CASE_1, CASE_2
])
def test_http_response_init(request, status_code, headers, body, expected):
    resp = HttpResponse(request, status_code, headers, body)
    for k, v in expected.items():
        assert getattr(resp, k) == v
