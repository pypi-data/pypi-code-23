"""Configuration helpers."""

# Copyright 2016-2018 ASI Data Science
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import six
import click

SHERLOCKML_ENV = os.getenv('SHERLOCKML_ENV', 'prod')


class CredentialsError(Exception):
    """Exception for errors reading credentials."""
    pass


def _get_subdomain():
    """Determine platform subdomain."""
    domain = os.getenv('SHERLOCKML_DOMAIN')
    if not domain:
        env = os.getenv('SHERLOCKML_ENV')
        if env == 'prod':
            domain = 'platform.asidata.science'
        elif env == 'staging':
            domain = 'platform-staging.asidata.science'
        else:
            try:
                domain = _get_credential_option('domain')
            except CredentialsError:
                domain = 'platform.asidata.science'
    return domain


def _get_protocol():
    """Determine platform protocol."""
    protocol = os.getenv('SHERLOCKML_PROTOCOL')
    if not protocol:
        try:
            protocol = _get_credential_option('protocol')
        except CredentialsError:
            protocol = 'https'
    return protocol


def _get_credentials_section(parser):
    section = 'default'
    env = os.getenv('SHERLOCKML_ENV')
    if env:
        if parser.has_section(env):
            section = env
        else:
            tpl = 'No section named "{}" found in credentials file'
            raise CredentialsError(tpl.format(env))
    return section


def url_for_service(service):
    """Return URL for the given service."""
    subdomain = _get_subdomain()
    protocol = _get_protocol()
    return '{}://{}.{}'.format(protocol, service, subdomain)


def casebook_url():
    """Return URL for Casebook."""
    return url_for_service('casebook')


def hudson_url():
    """Return URL for Hudson"""
    return url_for_service('hudson')


def galleon_url():
    """Return URL for Galleon."""
    return url_for_service('galleon')


def baskerville_url():
    """Return URL for Baskerville."""
    return url_for_service('baskerville')


def frontend_url(environment=SHERLOCKML_ENV):
    """Return URL for the SherlockML frontend in the given environment."""
    if environment == 'prod':
        return 'https://sherlockml.com'
    return 'https://{}.sherlockml.com'.format(environment)


def get_credentials():
    """Get a SherlockML client ID and client secret."""
    try:
        return _get_credentials_from_environ()
    except CredentialsError:
        return _get_credentials_from_file()


def _get_credentials_from_environ():
    """Get a SherlockML client ID and client secret from the environment."""
    try:
        client_id = os.environ['SHERLOCKML_CLIENT_ID']
    except KeyError:
        raise CredentialsError(
            'Missing SHERLOCKML_CLIENT_ID environment variable')
    try:
        client_secret = os.environ['SHERLOCKML_CLIENT_SECRET']
    except KeyError:
        raise CredentialsError(
            'Missing SHERLOCKML_CLIENT_SECRET environment variable')
    return client_id, client_secret


def _get_credential_option(option):
    """Get a credential option from a ConfigParser."""
    credentials_path = _get_credentials_path()
    parser = six.moves.configparser.SafeConfigParser()

    if not parser.read(credentials_path):
        raise CredentialsError('No credentials file found at {}'.format(
            credentials_path))

    section = _get_credentials_section(parser)
    try:
        return parser.get(section, option)
    except six.moves.configparser.NoSectionError:
        tpl = 'No section named "{}" found in credentials file'
        raise CredentialsError(tpl.format(section))
    except six.moves.configparser.NoOptionError:
        tpl = 'No "{}" key found in "{}" section of credentials file'
        raise CredentialsError(tpl.format(option, section))


def _credentials_file_path(directory):
    """Return the path to a credentials file."""
    xdg_config_home = os.environ.get('XDG_CONFIG_HOME')

    if not xdg_config_home:
        xdg_config_home = os.path.expanduser('~/.config')

    return os.path.join(xdg_config_home, directory, 'credentials')


def _get_credentials_path():
    """Get path to the credentials config file, warning on deprecated path."""
    deprecated_path = _credentials_file_path('sherlock')
    credentials_path = _credentials_file_path('sherlockml')

    if (os.path.exists(deprecated_path) and
            not os.path.exists(credentials_path)):
        template = ('The {} file is deprecated and will be ignored in '
                    'future.\n'
                    'You should move your credentials file to {}.\n')
        click.secho(template.format(deprecated_path, credentials_path),
                    err=True, fg='yellow')
        return deprecated_path
    return credentials_path


def _get_credentials_from_file():
    """Get a SherlockML client ID and client secret from the config file."""

    client_id = _get_credential_option('client_id')
    client_secret = _get_credential_option('client_secret')

    return client_id, client_secret
