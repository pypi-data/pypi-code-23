import tempfile
from contextlib import contextmanager
from os import path
from unittest import TestCase
from mock import patch, Mock
import textwrap

import sml.config


class TestConfig(TestCase):

    def test_config_read_default_credentials(self):
        config_content = textwrap.dedent("""\
        [default]
        client_id = client-id-default
        client_secret = client-secret-default
        """)
        with config_with_mock_credentials_file(config_content) as config:
            assert config.get_credentials() == ('client-id-default', 'client-secret-default')

    @patch('os.environ', {
        'SHERLOCKML_CLIENT_ID': 'client-id-from-env',
        'SHERLOCKML_CLIENT_SECRET': 'client-secret-from-env'
    })
    def test_credentials_from_env_default(self):
        config_content = textwrap.dedent("""\
        [default]
        client_id = client-id-default
        client_secret = client-secret-default
        """)
        with config_with_mock_credentials_file(config_content) as config:
            assert config.get_credentials() == (
                'client-id-from-env', 'client-secret-from-env')

    @patch('os.environ', {
        'SHERLOCKML_CLIENT_ID': 'client-id-from-env',
        'SHERLOCKML_CLIENT_SECRET': 'client-secret-from-env',
        'SHERLOCKML_ENV': 'staging'
    })
    @patch('sml.config.SHERLOCKML_ENV', 'staging')
    def test_credentials_from_env(self):
        config_content = textwrap.dedent("""\
        [default]
        client_id = client-id-default
        client_secret = client-secret-default
        [staging]
        client_id = client-id-staging
        client_secret = client-secret-staging
        """)
        with config_with_mock_credentials_file(config_content) as config:
            assert config.get_credentials() == (
                'client-id-from-env', 'client-secret-from-env')

    def test_default_domain_and_protocol(self):
        with config_with_mock_credentials_file('') as config:
            assert config.casebook_url() == 'https://casebook.platform.asidata.science'

    @patch('os.environ', {'SHERLOCKML_ENV': 'staging'})
    @patch('sml.config.SHERLOCKML_ENV', 'staging')
    def test_staging_domain_and_protocol(self):
        config_content = textwrap.dedent("""\
        [staging]
        client_id = client-id-staging
        client_secret = client-secret-staging
        domain = domain-staging
        protocol = protocol-staging
        """)
        with config_with_mock_credentials_file(config_content) as config:
            assert config.get_credentials() == ('client-id-staging', 'client-secret-staging')
            assert config.casebook_url() == 'protocol-staging://casebook.platform-staging.asidata.science'

    @patch('os.environ', {'SHERLOCKML_ENV': 'dummyenv'})
    @patch('sml.config.SHERLOCKML_ENV', 'dummyenv')
    def test_user_specified_domain_and_protocol(self):
        config_content = textwrap.dedent("""\
        [dummyenv]
        client_id = client-id-dummy-env
        client_secret = client-secret-dummy-env
        domain = domain
        protocol = protocol
        """)
        with config_with_mock_credentials_file(config_content) as config:
            assert config.get_credentials() == ('client-id-dummy-env', 'client-secret-dummy-env')
            assert config.casebook_url() == 'protocol://casebook.domain'

    @patch('os.environ', {
        'SHERLOCKML_DOMAIN': 'domain-from-env',
        'SHERLOCKML_PROTOCOL': 'protocol-from-env'
    })
    def test_domain_from_env_precedence_over_file(self):
        config_content = textwrap.dedent("""\
        [default]
        client_id = client-id-default
        client_secret = client-secret-default
        domain = domain-from-file
        protocol = protocol-from-file
        """)

        with config_with_mock_credentials_file(config_content) as config:
            assert config.casebook_url() == 'protocol-from-env://casebook.domain-from-env'

    @patch('os.environ', {'SHERLOCKML_ENV': 'staging'})
    @patch('sml.config.SHERLOCKML_ENV', 'staging')
    def test_missing_env_config_section(self):
        config_content = textwrap.dedent("""\
        [default]
        client_id = client-id-default
        client_secret = client-secret-default
        """)

        with config_with_mock_credentials_file(config_content) as config:
            with self.assertRaises(sml.config.CredentialsError) as context:
                config.get_credentials()
            expected_message = 'No section named "staging" ' \
                               'found in credentials file'
            self.assertTrue(str(context.exception) in expected_message)

    @patch('os.environ', {'SHERLOCKML_ENV': 'staging'})
    @patch('sml.config.SHERLOCKML_ENV', 'staging')
    def test_env_config_section_empty(self):
        config_content = textwrap.dedent("""\
        [default]
        client_id = client-id-default
        client_secret = client-secret-default
        [staging]
        """)
        with config_with_mock_credentials_file(config_content) as config:
            with self.assertRaises(sml.config.CredentialsError) as context:
                config.get_credentials()
            expected_message = 'No "client_id" key found in "staging" ' \
                               'section of credentials file'
            self.assertTrue(str(context.exception) in expected_message)


@contextmanager
def config_with_mock_credentials_file(content):
    with patch('sml.config._credentials_file_path', Mock()) as mock:
        with tempfile.NamedTemporaryFile() as credentials_file:
            tmp_path = path.realpath(credentials_file.name)
            mock.return_value = tmp_path
            credentials_file.write(bytearray(content, 'utf-8'))
            credentials_file.flush()
            sml.config._credentials_file_path = mock
            yield sml.config
