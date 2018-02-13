import os
import ssl
import json
import binascii
import http

from bgweb.profile.bgprofile import BGProfileUpdateError, BGProfile


class Auth0ConnexionError(BGProfileUpdateError):
    """
    Exception when updating the profile in the Auth0
    servers

    Args:
        message (str): error message
        status (int): status code of the HTTP response
        reason (str):  reason of the failure
    """

    def __init__(self, message, status=None, reason=None):
        self.message = message
        self.status = status
        self.reason = reason


class Auth0Profile(BGProfile):
    """
    BGProfile obtained from Auth0.
    """

    def __init__(self, user_id, profile, domain):

        self.domain = domain

        super(Auth0Profile, self).__init__(user_id, profile)

    def _process_profile(self, profile):
        """
        Get all the information from the profile obtained from Auth0.
        One extra field should be provided to the profile: 'token_id'.
        It represents the token obtained from the Aut0 after authentication
        succeed.

        Args:
            profile (dict): profile retrieved after login with Auth0

        Some fields are fist level items in the Auth0 profile. The others
        are stored in the user_metatdata field.
        Requires the token id to be able to update the user metatdata
        """
        self.email = profile.get('email', None)
        self.token_id = profile['token_id']
        self.name = profile.get('name')
        if self.name == self.email:
            self.name = profile.get('given_name', profile.get('nickname', self.name))
        self.email_verified = profile.get('email_verified', False)
        self.user_id = profile['user_id']
        self.metadata = profile.get('user_metadata', {})
        self.institution = self.metadata.get('institution', self.institution)
        self.terms = set(self.metadata.get('terms', self.terms))
        self.newsletter = self.metadata.get('newsletter', self.newsletter)
        self.rest_api_token = self.metadata.get('api_token', self.rest_api_token)

    def accept_terms(self, application):
        self._auth0_save('terms', application, 'add')
        self.terms = set(self.metadata.get('terms', {}))

    def reject_terms(self, application):
        self._auth0_save('terms', application, 'remove')
        self.terms = set(self.metadata.get('terms', {}))

    def accept_newsletter(self):
        self._auth0_save('newsletter', True)
        self.newsletter = self.metadata.get('newsletter', False)

    def reject_newsletter(self):
        self._auth0_save('newsletter', None)
        self.newsletter = self.metadata.get('newsletter', False)

    def update_institution(self, institution):
        self._auth0_save('institution', institution)
        self.institution = self.metadata.get('institution', None)

    def generate_rest_api_token(self):
        token = binascii.hexlify(os.urandom(10)).decode('utf-8')
        self._auth0_save('api_token', token)
        self.rest_api_token = self.metadata.get('api_token', None)

    def _auth0_save(self, field, value, action='replace'):
        """
        Updates the user metadata in the Auth0 database

        Args:
            field (str):
            value:
            action (str): 'replace' to replace the value of a field, 'add' to add a value
             to a list, 'remove' to remove a value from a list, 'reset' to set the field's value to None

        Raises:
            Auth0ConnexionError.

        """

        # TODO Remove unverified SSL context
        conn = http.client.HTTPSConnection(self.domain, context=ssl._create_unverified_context())
        if action == 'replace':
            metadata = {'user_metadata':{field:value}}
        elif action == 'add':
            values = self.metadata.get(field, [])
            if value in values:
                return
            else:
                values.append(value)
                metadata = {'user_metadata':{field: values}}
        elif action == 'remove':
            values = self.metadata.get(field, [])
            if value in values:
                values.remove(value)
                metadata = {'user_metadata':{field: values}}
            else:
                return
        elif action == 'reset':
            metadata = {'user_metadata': {field: None}}

        payload = json.dumps(metadata)

        headers = {
            'authorization': "Bearer {}".format(self.token_id),
            'content-type': "application/json"
        }

        conn.request("PATCH", "/api/v2/users/{}".format(self.user_id), payload, headers)

        res = conn.getresponse()
        data = res.read()
        data = data.decode("utf-8")

        conn.close()

        if res.status < 400:
            data = json.loads(data)
            self.metadata = data.get('user_metadata', {})
        else:
            raise Auth0ConnexionError(data, res.status, res.reason)
