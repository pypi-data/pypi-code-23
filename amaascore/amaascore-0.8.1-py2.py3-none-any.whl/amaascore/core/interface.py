from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime
import logging

import requests
from warrant.aws_srp import AWSSRP

from amaascore.config import ENDPOINTS, ConfigFactory, get_factory
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

    def __new__(cls, config, username=None, password=None, logger=None):
        cache_key = (config, username, password)
        cached = cls.__session_cache.get(cache_key)
        if not cached:
            cached = super(AMaaSPasswordSession, cls).__new__(cls)
            cls.__session_cache[cache_key] = cached

        return cached

    def __init__(self, config, username=None, password=None, logger=None):
        super(AMaaSPasswordSession, self).__init__(logger)
        self.username = username or config.username
        self.password = password or config.password
        self.aws = AWSSRP(
            username=self.username, password=self.password,
            pool_id=config.cognito_pool_id,
            pool_region=config.cognito_region,
            client_id=config.cognito_client_id,
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

    def __init__(self, endpoint_type, endpoint=None, environment=None, username=None, password=None,
                 config_filename=None, logger=None, session_token=None):
        self.logger = logger or logging.getLogger(__name__)
        if config_filename:
            config_factory = ConfigFactory(config_filename)
        else:
            config_factory = get_factory()

        self.api_config = config_factory.api_config(environment)

        self.endpoint_type = endpoint_type
        self.endpoint = self.get_endpoint(endpoint)
        if session_token:
            self.session = AMaaSTokenSession(session_token, logger=self.logger)
        else:
            self.session = AMaaSPasswordSession(
                config_factory.auth_config(environment),
                username=username, password=password,
                logger=self.logger,
            )

        self.json_header = {'Content-Type': 'application/json'}
        self.logger.info('Interface Created')

    def get_endpoint(self, endpoint=None):
        """Return interface URL endpoint."""
        base_url = self.api_config.api_url
        if not endpoint:
            if 'localhost' in base_url:
                endpoint = ''
            else:
                endpoint = ENDPOINTS[self.endpoint_type]

        endpoint = '/'.join([p.strip('/') for p in (base_url, endpoint)]).strip('/')
        self.logger.info("Using Endpoint: %s", endpoint)
        return endpoint
