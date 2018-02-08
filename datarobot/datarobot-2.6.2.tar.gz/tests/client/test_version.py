import json

import pytest
import responses

from datarobot.client import get_client

import mock


@pytest.yield_fixture
def client_version_mock():
    with mock.patch('datarobot.client._get_client_version') as mv:
        yield mv


class TestVersionCheck(object):

    @pytest.yield_fixture
    def server_version_mock(self):
        with mock.patch('datarobot.client._get_server_version') as mv:
            yield mv

    @pytest.yield_fixture(autouse=True)
    def no_global_client(self, default_config):
        with mock.patch('datarobot.client._global_client', None) as gc:
            yield gc

    def test_major_incompat(self, server_version_mock, client_version_mock):
        server_version_mock.return_value = '2.3.0'
        client_version_mock.return_value = '3.0.0'
        with pytest.raises(RuntimeError):
            get_client()

    @pytest.mark.usefixtures('known_warning')
    def test_minor_incompat(self, server_version_mock, client_version_mock):
        server_version_mock.return_value = '2.3.0'
        client_version_mock.return_value = '2.4.0'
        get_client()

    def test_server_can_be_ahead_of_client(self, server_version_mock, client_version_mock):
        server_version_mock.return_value = '2.4.0'
        client_version_mock.return_value = '2.3.0'
        get_client()


class TestServerVersion(object):

    @pytest.fixture
    def version_endpoint(self, default_config_endpoint):
        return default_config_endpoint + '/version/'

    @responses.activate
    @pytest.mark.usefixtures('default_config', 'known_warning')
    def test_version_does_not_exist(self, version_endpoint):
        """This situation happens if a user is using a client that is new
        enough to check for version on a server that doesn't have an endpoint
        to supply that version
        """
        responses.add(
            responses.GET,
            version_endpoint,
            status=404,
            body=''
        )

        get_client()

    @responses.activate
    @pytest.mark.usefixtures('default_config')
    def test_version_does_exist(self, version_endpoint, client_version_mock):
        client_version_mock.return_value = '2.4.0'

        responses.add(
            responses.GET,
            version_endpoint,
            status=200,
            body=json.dumps({'major': '2', 'minor': '4', 'versionString': '2.4.0'})
        )

        get_client()
