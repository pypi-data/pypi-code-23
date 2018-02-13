"""
BGProfile is the profile for the external
users that use our services.

Profile fields:
- id: user ID (email)
- name: user name
- email: user email
- institution: institution where the user belongs to
- newsletter: if the user is subscribed to our newsletter or not
- terms: set of the applications where the user has accepted the terms
- rest_api_token: token for APIs using REST
"""


import os
import binascii


class BGProfileError(Exception):
    """
    Exception produced by :class:`BGProfile`.
    Base class for other exceptions.

    Args:
        message (str): error message
    """

    def __init__(self, message):
        self.message = message


class BGProfileUpdateError(BGProfileError):
    """
    Exception produced when updating the profile
    fails
    """
    pass


class BGProfile:
    """
    Profile of the users that user our services. It serves as a base class for different implementations

    Args:
        user_id (str): user ID (unique identifier for each user
        profile: object from which the fields of the user profile are obtained

    """

    def __init__(self, user_id, profile):

        self.id = user_id
        self.name = None  # Name of the user to be shown in the Web App
        self.email = None
        self.metadata = None
        self.institution = None
        self.newsletter = False
        self.rest_api_token = None
        self.terms = set()
        self._process_profile(profile)

    def _process_profile(self, profile):
        """
        Process the received profile to obtain the fields for the BGProfile

        Args:
            profile:

        """
        raise NotImplementedError

    def accept_terms(self, application):
        """
        Add an application to the ones that the user has already accepted the terms

        Args:
            application (str): application name

        """
        self.terms.add(application)

    def reject_terms(self, application):
        """
        Remove application from the ones that the user has already accepted the terms

        Args:
            application (str): application name

        """
        self.terms.discard(application)

    def accept_newsletter(self):
        """
        User accepts to receive the newsletter
        """
        self.newsletter = True

    def reject_newsletter(self):
        """
        User rejects to receive the newsletter
        """
        self.newsletter = False

    def update_institution(self, institution):
        """
        Change the institution of the user

        Args:
            institution (str): institution

        """
        self.institution = institution

    def terms_accepted(self, application):
        """

        Args:
            application (str): application name

        Returns:
            bool. Whether the user has accepted the term for certain application

        """
        return application in self.terms

    def generate_rest_api_token(self):
        """
        Generate a token to be used in the REST API

        """
        self.rest_api_token = binascii.hexlify(os.urandom(10)).decode('utf-8')
