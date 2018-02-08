from .base import BaseBackend
from ddsc.core.ddsapi import DataServiceApi, DataServiceAuth
from requests.exceptions import HTTPError
from ..utils import check_jwt_token, get_local_user, make_auth_config, save_dukeds_token
from jwt import InvalidTokenError

class DukeDSAuthBackend(BaseBackend):
    """
    Backend for DukeDS Auth
    Conveniently, the keys used by DukeDS user objects are a superset of the django ones,
    so we rely on the filtering in the base class
    """
    def __init__(self):
        self.failure_reason = None

    def harmonize_user_details(self, details):
        """
        Overrides harmonize_user_details in BaseBackend to append @duke.edu to usernames from DukeDS
        :param details: incoming dictionary of user details
        :return: details harmonized for a django user object
        """
        details = super(DukeDSAuthBackend, self).harmonize_user_details(details)
        # For DukeDS, we need to append @duke.edu to username
        if 'username' in details:
            details['username'] = '{}@duke.edu'.format(details['username'])
        return details

    @staticmethod
    def harmonize_dukeds_user_details(details):
        """
        Given a dict of
        :param details:
        :return:
        """
        mapping = dict((k, k) for k in ('full_name','email',))
        return BaseBackend.harmonize_dict(mapping,details)

    def authenticate(self, token):
        """
        Authenticate a user with a DukeDS API token. Returns None if no user could be authenticated,
        and sets the errors list with the reasons
        :param token: A JWT token
        :return: an authenticated, populated user if found, or None if not.
        """
        self.failure_reason = None
        # 1. check if token is valid for this purpose
        try:
            check_jwt_token(token)
        except InvalidTokenError as e:
            self.failure_reason = e
            # Token may be expired or may not be valid for this service, so return None
            return None

        # Token is a JWT and not expired
        # 2. Check if token exists in database
        user = get_local_user(token)
        if user:
            # token matched a user, return it
            return user

        # 3. Token appears valid but we have not seen it before.
        # Fetch user details from DukeDS

        config = make_auth_config(token)
        auth = DataServiceAuth(config)
        api = DataServiceApi(auth, config.url)
        try:
            response = api.get_current_user()
            response.raise_for_status()
            user_dict = response.json()
        except HTTPError as e:
            self.failure_reason = e
            return None
        # DukeDS shouldn't stomp over existing user details
        user = self.save_user(user_dict, False)

        # 4. Have a user, save their token
        save_dukeds_token(user, token)
        self.handle_new_user(user, user_dict)
        return user

    def handle_new_user(self, user, details):
        """
        Stub method to allow custom behavior for new DukeDS users
        :param user: A django model user
        :param raw_user_dict: user details from DukeDS API, including their id
        """
        pass
