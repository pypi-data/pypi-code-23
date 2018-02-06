import mock
import os

import pytest
import six
import responses
import tempfile
import unittest

import datarobot as dr
from datarobot.rest import RESTClientObject
from datarobot.client import set_client, get_client, Client
from datarobot.enums import DEFAULT_TIMEOUT
from datarobot.errors import AppPlatformError
from .utils import SDKTestcase

if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch


class TestClient(object):

    @pytest.fixture(autouse=True)
    def empty_client(self):
        set_client(None)

    @pytest.yield_fixture(autouse=True)
    def no_version_check(self):
        with mock.patch('datarobot.client._version_warning'):
            yield

    def test_instantiation(self):
        """
        Basic client installation.
        """
        client = Client(token='t-token', endpoint='https://host_name.com')
        assert get_client() is client

    @mock.patch('datarobot.client._file_exists', return_value=False)
    def test_instantiation_without_env(self, mock_file_args):
        """
        Basic client installation by get_client without configuration.
        """
        with mock.patch(
            'os.environ',
                {'DATAROBOT_ENDPOINT': 'https://host_name.com'}):
            with pytest.raises(ValueError):
                get_client()

    @mock.patch('datarobot.client._file_exists')
    def test_no_endpoint_fails(self, mock_file_exists):
        mock_file_exists.return_value = False
        with mock.patch('os.environ', {}):
            with pytest.raises(ValueError):
                Client(token='NOTATOKEN')

    def test_token_and_endpoint_is_okay(self):
        Client(token='token', endpoint='https://need_an_endpoint.com')

    def test_re_instantiation(self):
        """
        Client re installation.
        """
        previous = Client(token='t-****', endpoint='https://end.com')
        old_client = set_client(RESTClientObject(auth=('u-**********', 'p-******'),
                                                 endpoint='https://host_name.com'))
        assert previous is old_client

    @responses.activate
    def test_recognizing_domain_on_instance(self):
        raw = """{"api_token": "some_token"}"""
        responses.add(responses.POST,
                      'https://host_name.com/api/v2/api_token/',
                      body=raw,
                      status=201,
                      content_type='application/json')
        set_client(RESTClientObject(auth=('u-**********', 'p-******'),
                                    endpoint='https://host_name.com/api/v2'))
        restored_client = get_client()
        assert restored_client.domain == 'https://host_name.com'

    @mock.patch('datarobot.client._file_exists', return_value=False)
    def test_instantiation_from_env(self, mock_file_exists):
        """
        Test instantiation with creds from virtual environment
        """
        with patch.dict(
            'os.environ',
            {'DATAROBOT_API_TOKEN': 'venv_token',
             'DATAROBOT_ENDPOINT': 'https://host_name.com'}):
            rest_client = get_client()
            assert rest_client.token == 'venv_token'
            assert rest_client.endpoint == 'https://host_name.com'

        set_client(None)

        with patch.dict(
            'os.environ',
            {'DATAROBOT_API_TOKEN': 'venv_token',
             'DATAROBOT_ENDPOINT': 'https://host_name.com'}):
            rest_client = get_client()
            assert rest_client.token == 'venv_token'
            assert rest_client.connect_timeout == DEFAULT_TIMEOUT.CONNECT

    def test_instantiation_from_file_with_wrong_path(self):
        with patch.dict('os.environ', {'DATAROBOT_CONFIG_FILE': './tests/fixtures/.datarobotrc'}):
            with pytest.raises(ValueError):
                get_client()

    def test_instantiation_from_yaml_file_api_token(self):
        file_data = ('token: fake_token\n'
                     'endpoint: https://host_name.com')
        config_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        try:
            with open(config_file.name, mode='w') as config:
                config.write(file_data)
            fake_environ = {'DATAROBOT_CONFIG_FILE': config_file.name}
            with patch('os.environ', fake_environ):
                rest_client = get_client()
            assert rest_client.token == 'fake_token'
            assert rest_client.endpoint == 'https://host_name.com'
            assert rest_client.connect_timeout == DEFAULT_TIMEOUT.CONNECT
        finally:
            os.remove(config_file.name)

    def test_instantiation_from_yaml_file_set_timeout(self, temporary_file):
        connect_timeout = 55
        file_data = ('token: fake_token\n'
                     'endpoint: https://host_name.com\n'
                     'connect_timeout: {}').format(connect_timeout)
        with open(temporary_file, mode='w') as config:
            config.write(file_data)
        fake_environ = {'DATAROBOT_CONFIG_FILE': temporary_file}
        with patch('os.environ', fake_environ):
            rest_client = get_client()
        assert rest_client.connect_timeout == connect_timeout

    def test_client_from_codeline(self):
        Client(token='some_token',
               endpoint='https://endpoint.com')
        c = get_client()
        assert c.token == 'some_token'
        assert c.endpoint == 'https://endpoint.com'
        assert c.connect_timeout == DEFAULT_TIMEOUT.CONNECT

    def test_client_from_codeline_set_timeout(self):
        connect_timeout = 55
        Client(token='some_token', endpoint='https://endpoint.com', connect_timeout=connect_timeout)
        c = get_client()
        assert c.connect_timeout == connect_timeout

    def test_client_user_agent(self):
        with patch('platform.system') as mock_system, \
             patch('platform.release') as mock_release, \
             patch('platform.machine') as mock_machine:
            mock_system.return_value = 'Prince'
            mock_release.return_value = 'Party'
            mock_machine.return_value = 'x19_99'
            header = RESTClientObject._make_user_agent_header()
        expected_agent = 'DataRobotPythonClient/{} (Prince Party x19_99)'.format(dr.__version__)
        assert header == {'User-Agent': expected_agent}

    def test_client_user_agent_with_suffix(self):
        suffix = "Blamo/8.23 (6.30)"
        orig = RESTClientObject._make_user_agent_header()
        with_suffix = RESTClientObject._make_user_agent_header(suffix=suffix)
        assert with_suffix['User-Agent'].startswith(orig['User-Agent'])
        assert with_suffix['User-Agent'].endswith(' ' + suffix)


class RestErrors(SDKTestcase):

    @responses.activate
    def test_404_plain_text(self):
        """
        Bad request in plain text
        """
        raw = "Not Found"

        responses.add(responses.GET, 'https://host_name.com/projects/404',
                      body=raw, status=404, content_type='text/plain')

        client = get_client()

        with self.assertRaises(AppPlatformError) as app_error:
            client.get('projects/404')

        self.assertEqual(str(app_error.exception),
                         '404 client error: Not Found')

    @responses.activate
    def test_404_json(self):
        """
        Bad request with datarobot reason in json
        """
        raw = """
        {"message": "Not Found"}
        """

        responses.add(responses.GET, 'https://host_name.com/projects/404',
                      body=raw, status=404, content_type='application/json')

        client = get_client()

        with self.assertRaises(AppPlatformError) as app_error:
            client.get('projects/404')

        exception_message = str(app_error.exception)
        self.assertIn('404 client error', exception_message)
        self.assertIn('Not Found', exception_message)

    @responses.activate
    def test_500_json(self):
        """
        Bad request with datarobot reason in json
        """
        raw = """
        {"message": "Not Found"}
        """

        responses.add(responses.GET, 'https://host_name.com/projects/500',
                      body=raw, status=500, content_type='application/json')

        client = get_client()

        with self.assertRaises(AppPlatformError) as app_error:
            client.get('projects/500')

        exception_message = str(app_error.exception)
        self.assertIn('500 server error', exception_message)
        self.assertIn('Not Found', exception_message)

    @responses.activate
    def test_other_errors(self):
        """
        Other errors
        """
        raw = """
        {"message": "Bad response"}
        """

        responses.add(responses.GET,
                      'https://host_name.com/projects/500',
                      body=raw, status=500, content_type='application/json')

        client = get_client()

        with self.assertRaises(AppPlatformError) as app_error:
            client.get('projects/500')
            self.assertEqual(str(app_error.exception),
                             'Connection refused: '
                             'https://host_name.com/projects/500')


class TestClientAttributes(unittest.TestCase):

    def test_main_useful_things_under_datarobot(self):
        """To lower the intimidation factor, let's try to limit the objects
        that show up at the root of datarobot

        This way, when they are in IPython and do tab-completion they get a
        sense for what is available to tinker with at the top level
        """
        known_names = {'Project',
                       'Model',
                       'DatetimeModel',
                       'PrimeModel',
                       'BlenderModel',
                       'FrozenModel',
                       'Ruleset',
                       'Blueprint',
                       'BlueprintTaskDocument',
                       'BlueprintChart',
                       'ModelBlueprintChart',
                       'ModelJob',
                       'PredictJob',
                       'Job',
                       'PredictionDataset',
                       'PrimeFile',
                       'QUEUE_STATUS',
                       'Client',
                       'AUTOPILOT_MODE',
                       'AppPlatformError',
                       'utils',
                       'errors',
                       'models',
                       'client',
                       'rest',
                       'async',
                       'SCORING_TYPE',
                       'Featurelist',
                       'ModelingFeaturelist',
                       'Feature',
                       'ModelingFeature',
                       'helpers',
                       'RandomCV',
                       'StratifiedCV',
                       'GroupCV',
                       'UserCV',
                       'RandomTVH',
                       'UserTVH',
                       'StratifiedTVH',
                       'GroupTVH',
                       'DatetimePartitioning',
                       'DatetimePartitioningSpecification',
                       'BacktestSpecification',
                       'partitioning_methods',
                       'AdvancedOptions',
                       'VERBOSITY_LEVEL',
                       'enums',
                       'ImportedModel',
                       'ReasonCodesInitialization',
                       'ReasonCodes',
                       'RatingTable',
                       'RatingTableModel',
                       'TARGET_TYPE',
                       'TrainingPredictions',
                       'TrainingPredictionsJob',
                       }

        found_names = {name for name in dir(dr)
                       if not name.startswith('_')}
        assert found_names == known_names


@pytest.yield_fixture
def mock_os():
    with patch('datarobot.client.os', autospec=True) as m:
        yield m


@pytest.yield_fixture
def mock_file_exists():
    with patch('datarobot.client._file_exists') as m:
        yield m


@pytest.yield_fixture
def mock_os_environ():
    with patch('datarobot.client.os.environ') as m:
        yield m
