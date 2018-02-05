"""prosper.datareader.intrinio.auth: handle authentication/validation"""

import requests

from .. import exceptions
from .. import config

BASE_URL = 'https://api.intrinio.com/'
class IntrinioHelper(object):
    """parent class for handling requests to Intrininio

    Notes:
        See https://intrinio.com/account for account keys

    Args:
        username (str): username for direct-auth
        password (str): password for direct-auth
        public_key (str): API key for indirect access

    Raises:
        InvalidAuth: will not be able to access Intrinio feeds

    """

    def __init__(self, username='', password='', public_key='',):
        self.__user = username
        self.__password = password
        self.__public_key = public_key

        if not bool(self):
            raise exceptions.InvalidAuth('Lacking required authentication')

    def request(self, route, params=None, headers=None):
        """empty metaclass for handling requests"""
        raise NotImplementedError()

    def __bool__(self):
        """validate acceptable auth pattern"""
        if all([self.__user, self.__password, self.__public_key]):
            # either/or, not both auth types
            return False

        if self.__user and self.__password:
            # direct auth method
            self.request = self._direct_auth_request
            return True

        if self.__public_key:
            # public-key method
            self.request = self._public_key_request
            return True

        return False

    def _direct_auth_request(self, route, params=None, headers=None):
        """handle HTTP request for direct-auth

        Args:
            url (str): url of endpoint to fetch
            params (dict): param args for endpoint request
            headers (dict): headers for endpoint request

        Returns:
            dict: JSON-parsed response from endpoint

        Raises:
            requests.exceptions: connection/HTTP errors

        """
        req = requests.get(
            url=BASE_URL + route,
            params=params,
            headers=headers,
            auth=(self.__user, self.__password),
        )
        req.raise_for_status()
        return req.json()

    def _public_key_request(self, route, params=None, headers=None):
        """handle HTTP request for public-key

        Args:
            url (str): url of endpoint to fetch
            params (dict): param args for endpoint request
            headers (dict): headers for endpoint request

        Returns:
            dict: JSON-parsed response from endpoint

        Raises:
            requests.exceptions: connection/HTTP errors

        """
        if not headers:
            headers = {}

        headers = {**headers, 'X-Authorization-Public-Key':self.__public_key}
        req = requests.get(
            url=BASE_URL + route,
            params=params,
            headers=headers,
        )
        req.raise_for_status()
        return req.json()
