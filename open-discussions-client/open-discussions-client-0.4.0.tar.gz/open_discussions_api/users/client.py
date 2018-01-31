"""Users API"""
from urllib.parse import quote

from open_discussions_api.base import BaseApi

SUPPORTED_PROFILE_ATTRIBUTES = (
    'name',
    'image',
    'image_small',
    'image_medium',
    'email_optin',
)


class UsersApi(BaseApi):
    """Users API"""

    def list(self):
        """
        Returns a list of users

        Returns:
            requests.Response: A response containing the data for all users in open-discussions
        """
        return self.session.get(self.get_url("/users/"))

    def get(self, username):
        """
        Gets a specific user

        Args:
            username (str): The username for the user

        Returns:
            requests.Response: A response containing the user's data
        """
        return self.session.get(self.get_url("/users/{}/").format(quote(username)))

    def create(self, email=None, profile=None):
        """
        Creates a new user

        Args:
            email (str): the user's email
            profile (dict): attributes used in creating the profile. See SUPPORTED_USER_ATTRIBUTES for a list.

        Returns:
            requests.Response: A response containing the newly created profile data
        """
        if not profile:
            raise AttributeError("No fields provided to create")

        for key in profile:
            if key not in SUPPORTED_PROFILE_ATTRIBUTES:
                raise AttributeError("Profile attribute {} is not supported".format(key))

        payload = {
            'profile': profile or {},
        }

        if email is not None:
            payload['email'] = email

        return self.session.post(
            self.get_url("/users/"),
            json=payload,
        )

    def update(self, username, email=None, profile=None):
        """
        Gets a specific user

        Args:
            username (str): The username of the user
            profile (dict):
                Attributes of the profile to update for that user. See SUPPORTED_USER_ATTRIBUTES for a valid list.

        Returns:
            requests.Response: A response containing the updated user profile data
        """
        if not profile:
            raise AttributeError("No fields provided to update")

        for key in profile:
            if key not in SUPPORTED_PROFILE_ATTRIBUTES:
                raise AttributeError("Profile attribute {} is not supported".format(key))

        payload = {
            'profile': profile or {},
        }

        if email is not None:
            payload['email'] = email

        return self.session.patch(
            self.get_url("/users/{}/".format(quote(username))),
            json=payload,
        )
