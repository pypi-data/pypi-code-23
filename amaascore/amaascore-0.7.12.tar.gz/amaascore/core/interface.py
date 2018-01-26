from __future__ import absolute_import, division, print_function, unicode_literals

from configparser import ConfigParser, NoSectionError
from datetime import datetime
import logging
from os.path import expanduser, join
from os import environ

import requests
from warrant.aws_srp import AWSSRP

from amaascore.config import ENVIRONMENT, ENDPOINTS, CONFIGURATIONS
from amaascore.exceptions import AMaaSException


class AMaaSSession(object):

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.refresh_period = 45 * 60  # minutes * seconds
        self.last_authenticated = None
        self.session = requests.Session()

    def needs_refresh(self):
        if not (self.last_authenticated and
                (datetime.utcnow() - self.last_authenticated).seconds < self.refresh_period):
            return True
        else:
            return False

    def put(self, url, data=None, **kwargs):
        # Add a refresh
        if self.last_authenticated and not self.needs_refresh():
            return self.session.put(url=url, data=data, **kwargs)
        else:
            raise AMaaSException('Not Authenticated')

    def post(self, url, data=None, **kwargs):
        # Add a refresh
        if self.last_authenticated and not self.needs_refresh():
            return self.session.post(url=url, data=data, **kwargs)
        else:
            raise AMaaSException('Not Authenticated')

    def delete(self, url, **kwargs):
        # Add a refresh
        if self.last_authenticated and not self.needs_refresh():
            return self.session.delete(url=url, **kwargs)
        else:
            raise AMaaSException('Not Authenticated')

    def get(self, url, **kwargs):
        # Add a refresh
        if self.last_authenticated and not self.needs_refresh():
            return self.session.get(url=url, **kwargs)
        else:
            raise AMaaSException('Not Authenticated')

    def patch(self, url, data=None, **kwargs):
        # Add a refresh
        if self.last_authenticated and not self.needs_refresh():
            return self.session.patch(url=url, data=data, **kwargs)
        else:
            raise AMaaSException('Not Authenticated')


class AMaaSPasswordSession(AMaaSSession):

    __session_cache = {}

    def __new__(cls, environment_config, username=None, password=None, logger=None):
        cache_key = (environment_config, username, password)
        cached = cls.__session_cache.get(cache_key)
        if not cached:
            cached = super(AMaaSPasswordSession, cls).__new__(cls)
            cls.__session_cache[cache_key] = cached

        return cached

    def __init__(self, environment_config, username=None, password=None, logger=None):
        super(AMaaSPasswordSession, self).__init__(logger)
        self.username = username
        self.password = password
        self.aws = AWSSRP(
            username=self.username, password=self.password,
            pool_id=environment_config.cognito_pool,
            client_id=environment_config.cognito_client_id,
            pool_region=environment_config.cognito_region,
        )

        if self.needs_refresh():
            self.login()

    def login(self):
        try:
            self.logger.info("Attempting login for: %s", self.username)
            tokens = self.aws.authenticate_user().get('AuthenticationResult')
            self.logger.info("Login successful")
            self.last_authenticated = datetime.utcnow()
            self.session.headers.update({'Authorization': tokens.get('IdToken')})
        except self.aws.client.exceptions.NotAuthorizedException:
            self.logger.exception("Login failed")
            self.last_authenticated = None


class AMaaSTokenSession(AMaaSSession):

    def __init__(self, session_token, logger=None):
        super(AMaaSTokenSession, self).__init__(logger)
        self.session_token = session_token
        self.logger.info("Skipping login since session token is provided.")
        self.session.headers.update({'Authorization': self.session_token})
        self.last_authenticated = datetime.utcnow()


class Interface(object):
    """
    Currently this class doesn't do anything - but I anticipate it will be needed in the future.
    """

    def __init__(self, endpoint_type, endpoint=None, environment=ENVIRONMENT, username=None, password=None,
                 config_filename=None, logger=None, session_token=None):
        self.logger = logger or logging.getLogger(__name__)
        self.config_filename = config_filename
        self.endpoint_type = endpoint_type
        self.environment = environment
        self.environment_config = CONFIGURATIONS.get(environment)
        self.endpoint = endpoint or self.get_endpoint()
        self.json_header = {'Content-Type': 'application/json'}
        if session_token:
            self.session = AMaaSTokenSession(session_token, logger=self.logger)
        else:
            username = username or environ.get('AMAAS_USERNAME') or self.read_config('username')
            password = password or environ.get('AMAAS_PASSWORD') or self.read_config('password')
            self.session = AMaaSPasswordSession(
                environment_config=self.environment_config,
                username=username, password=password,
                logger=self.logger,
            )

        self.logger.info('Interface Created')

    def get_endpoint(self):
        if self.environment == 'local':
            return self.environment_config.base_url
        if self.environment not in CONFIGURATIONS:
            raise KeyError('Invalid environment specified.')

        base_url = self.environment_config.base_url
        endpoint = ENDPOINTS.get(self.endpoint_type)
        api_version = self.environment_config.api_version
        if not endpoint:
            raise KeyError('Cannot find endpoint')
        endpoint = '/'.join([base_url, api_version, endpoint])
        self.logger.info("Using Endpoint: %s", endpoint)
        return endpoint

    @staticmethod
    def generate_config_filename():
        home = expanduser("~")
        return join(home, '.amaas.cfg')

    def read_config(self, option):
        if self.config_filename is None:
            self.config_filename = self.generate_config_filename()
        parser = ConfigParser()
        parser.read(self.config_filename)
        try:
            option = parser.get(section='auth', option=option)
        except NoSectionError:
            raise AMaaSException('Invalid AMaaS config file')
        return option
