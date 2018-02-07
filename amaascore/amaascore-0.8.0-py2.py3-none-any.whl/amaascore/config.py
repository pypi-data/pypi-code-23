"""Configuration for connecting to the AMaaS API."""
from __future__ import absolute_import
from collections import namedtuple
from configparser import ConfigParser, Error as ConfigParserError
import os
import re

from .exceptions import ConfigurationError, MissingConfigurationError


ENDPOINTS = {
    'asset_managers': 'assetmanager',
    'assets': 'asset',
    'books': 'book',
    'corporate_actions': 'corporateaction',
    'fundamentals': 'fundamental',
    'market_data': 'marketdata',
    'monitor': 'monitor',
    'parties': 'party',
    'transactions': 'transaction'
}


arn_re = re.compile(
    r'arn:(?P<partition>[\w-]+):(?P<service>[\w-]+):(?P<region>[\w-]*):(?P<account_id>\d*):'
    r'((?P<resourcetype>[\w-]*)[/:])?'
    r'(?P<resource>\S*)'
)


APIConfig = namedtuple('APIConfig', ['api_url'])


AuthConfig = namedtuple('AuthConfig', [
    'username', 'password',
    'cognito_pool_id', 'cognito_region', 'cognito_client_id',
])


class ConfigFactory(object):
    """Factory for building config object."""

    known_api_configurations = {
        'prod': APIConfig(api_url='https://api.amaas.com/sg1.0/'),
        'staging': APIConfig(api_url='https://api-staging.amaas.com/v1.0/'),
        'dev': APIConfig(api_url='https://api-dev.amaas.com/v1.0/'),
        'local': APIConfig(api_url='http://localhost:8000/'),
    }

    known_auth_configurations = {
        'prod': dict(
            cognito_pool_id='ap-southeast-1_0LilJdUR3',
            cognito_region='ap-southeast-1',
            cognito_client_id='7b7kt883veb7rr2toolj1ukp6j',
        ),
        'staging': dict(
            cognito_pool_id='ap-southeast-1_De6j7TWIB',
            cognito_region='ap-southeast-1',
            cognito_client_id='2qk35mhjjpk165vssuqhqoi1lk',
        ),
        'dev': dict(
            cognito_pool_id='ap-southeast-1_De6j7TWIB',
            cognito_region='ap-southeast-1',
            cognito_client_id='2qk35mhjjpk165vssuqhqoi1lk',
        ),
        'local': dict(
            cognito_pool_id='ap-southeast-1_De6j7TWIB',
            cognito_region='ap-southeast-1',
            cognito_client_id='2qk35mhjjpk165vssuqhqoi1lk',
        ),
    }

    def __init__(self, config_filepath=None):
        """Create new config factory."""
        # Read config file
        config_files = [config_filepath] if config_filepath else []
        config_files.extend([
            '.amaas.cfg',
            os.path.expanduser(os.path.join('~', '.amaas.cfg')),
            os.path.join('', 'etc', 'amaas.cfg'),
        ])
        parser = ConfigParser()
        parser.read(config_files)
        self.file_config = parser

    def lookup(self, section, name):
        """Lookup config value."""
        value = os.environ.get('AMAAS_{}'.format(name.upper()))
        if value:
            return value

        try:
            value = self.file_config.get(section, name)
        except ConfigParserError:
            pass
        else:
            if value:
                return value

        raise MissingConfigurationError(section, name)

    def api_config(self, stage=None):
        """Create api config based on stage."""
        if stage in self.known_api_configurations:
            return self.known_api_configurations[stage]

        if not stage:
            section = 'stages.live'
            api_url = 'https://api.amaas.com/'
        else:
            section = 'stages.{}'.format(stage)
            try:
                api_url = self.lookup(section, 'api_url')
            except ConfigurationError:
                api_url = 'https://api-{}.dev.amaas.com/'.format(stage)

        return APIConfig(api_url)

    def auth_config(self, stage=None):
        """Create auth config based on stage."""
        if stage:
            section = 'stages.{}'.format(stage)
        else:
            section = 'stages.live'

        try:
            username = self.lookup(section, 'username')
            password = self.lookup(section, 'password')
        except MissingConfigurationError:
            username = self.lookup('auth', 'username')
            password = self.lookup('auth', 'password')

        if stage in self.known_auth_configurations:
            return AuthConfig(
                username, password,
                **self.known_auth_configurations[stage]
            )

        try:
            cognito_pool_id = self.lookup(section, 'cognito_pool_id')
            cognito_region = self.lookup(section, 'cognito_region')
        except MissingConfigurationError:
            m = arn_re.match(self.lookup(section, 'cognito_pool'))
            if not m:
                raise ConfigurationError('Cognito Pool value must be an ARN')

            cognito_pool_id = m.group('resource')
            cognito_region = m.group('region')

        cognito_client_id = self.lookup(stage, 'cognito_client_id')
        return AuthConfig(
            username, password,
            cognito_pool_id, cognito_region, cognito_client_id,
        )


_global_config = None


def get_factory():
    """Get global config factory."""
    global _global_config
    if not _global_config:
        _global_config = ConfigFactory()

    return _global_config
