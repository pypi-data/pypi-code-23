import httplib
import json
import uuid

from furl import furl
import pytest
from pytest_localserver.http import WSGIServer
from werkzeug import Request
from werkzeug import Response


class FestungApp(WSGIServer):
    def __init__(self, *args, **kwargs):
        kwargs.update(application=self)
        super(FestungApp, self).__init__(*args, **kwargs)
        self.requests = []
        self.responses = []

    @Request.application
    def __call__(self, request):
        try:
            response = self.responses[len(self.requests)]
        except IndexError:
            response = Response("No prepared response")
            response.status_code = httplib.NOT_IMPLEMENTED
            return response

        self.requests.append(request)
        return response

    def add_response(self, data, status=None, headers=None):
        response = Response(data)
        response.status_code = status or httplib.OK
        response.headers = headers or {'Content-Type': 'text/html; charset=UTF-8'}
        self.responses.append(response)

    def add_json_response(self, data, status=httplib.OK):
        headers = {'Content-Type': 'application/json'}
        self.add_response(json.dumps(data), status=status, headers=headers)

    def add_empty_response(self):
        self.add_response(None, status=httplib.NO_CONTENT)

    @property
    def json_requests(self):
        return [json.loads(r.get_data()) for r in self.requests]


@pytest.fixture
def festung():
    server = FestungApp()
    server.start()
    try:
        yield server
    finally:
        server.stop()


@pytest.fixture
def festung_url(festung):
    return furl(festung.url).set(scheme='festung').url


@pytest.fixture
def database():
    return uuid.uuid4().hex


@pytest.fixture
def password():
    return uuid.uuid4().hex


@pytest.fixture(params=[''])
def query_string(request):
    return request.param


@pytest.fixture
def database_url(festung_url, password, database, query_string):
    url = furl(festung_url)
    assert url.username is None and url.password is None
    return url.set(password=password, path=database, query=query_string).remove(fragment=True).url
