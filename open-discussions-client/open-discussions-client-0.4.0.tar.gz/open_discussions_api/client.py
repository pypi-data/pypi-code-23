"""open-discussions api client"""
import requests

from open_discussions_api.users.client import UsersApi
from open_discussions_api.utils import get_token
from open_discussions_api.channels.client import ChannelsApi


class OpenDiscussionsApi:
    """
    A client for speaking with open-discussions

    Args:
        secret (str): the JWT secret
        base_url (str): the base API url
        username (str): the username to use for the token
        roles (list(str)): the list of roles the user headers
        version (str): the version of the API to use
    """

    def __init__(self, secret, base_url, username, roles=None, version="v0"):  # pylint: disable=too-many-arguments
        if not secret:
            raise AttributeError("secret is required")
        if not base_url:
            raise AttributeError("base_url is required")

        self.base_url = base_url
        self.secret = secret
        self.version = version
        self.username = username
        self.roles = roles or []

    def _get_session(self):
        """
        Gets an initial session

        Returns:
            requests.Session: default session
        """
        # NOTE: this method is a hook to allow substitution of the base session via mocking
        return requests.session()

    def _get_authenticated_session(self):
        """
        Returns an object to make authenticated requests. See python `requests` for the API.

        Returns:
            requests.Session: authenticated session
        """
        token = get_token(self.secret, self.username, self.roles)
        session = self._get_session()
        session.headers.update({
            'Authorization': 'Bearer {}'.format(token),
            'Content-Type': 'application/json',
        })
        return session

    @property
    def users(self):
        """
        Users API

        Returns:
            open_discussions_api.users.client.UsersApi: configured users api
        """
        return UsersApi(self._get_authenticated_session(), self.base_url, self.version)

    @property
    def channels(self):
        """
        Channels API
        """
        return ChannelsApi(self._get_authenticated_session(), self.base_url, self.version)
