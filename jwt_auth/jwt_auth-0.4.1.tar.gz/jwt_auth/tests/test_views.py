from django.test import TestCase

from calendar import timegm
from datetime import datetime, timedelta
import time
from jwt_auth.models import Staff
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_jwt import utils, views
from jwt_auth.settings import api_settings, DEFAULTS


User = Staff

NO_CUSTOM_USER_MODEL = 'Custom User Model only supported after Django 1.5'

orig_datetime = datetime


def jwt_response_payload_handler(token, user=None, request=None):
    """
    Returns the response data for both the login and refresh views.
    Override to return a custom response such as including the
    serialized representation of the User.
    Example:
    def jwt_response_payload_handler(token, user=None, request=None):
        return {
            'token': token,
            'user': UserSerializer(user, context={'request': request}).data
        }
    """
    return {
        'email': 'jpueblo@example.com',
        'token': token
    }


def get_jwt_secret(user):
    return user.jwt_secret


class BaseTestCase(TestCase):

    def setUp(self):
        self.email = 'jpueblo@example.com'
        self.username = 'jpueblo'
        self.password = 'password'
        self.user = User.objects.create_staff(
            self.email, self.password, confirm_password=self.password)

        self.data = {
            'email': self.email,
            'password': self.password
        }


class TestCustomResponsePayload(BaseTestCase):

    def setUp(self):
        self.original_handler = views.jwt_response_payload_handler
        views.jwt_response_payload_handler = jwt_response_payload_handler
        return super(TestCustomResponsePayload, self).setUp()

    def test_jwt_login_custom_response_json(self):
        """
        Ensure JWT login view using JSON POST works.
        """
        client = APIClient(enforce_csrf_checks=False)

        response = client.post('/api-auth/', self.data, format='json')

        decoded_payload = utils.jwt_decode_handler(response.data['token'])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(decoded_payload['email'], self.email)

    def tearDown(self):
        views.jwt_response_payload_handler = self.original_handler


class ObtainJSONWebTokenTests(BaseTestCase):

    def test_jwt_login_json(self):
        """
        Ensure JWT login view using JSON POST works.
        """
        client = APIClient(enforce_csrf_checks=True)

        response = client.post('/api-auth/', self.data, format='json')

        decoded_payload = utils.jwt_decode_handler(response.data['token'])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(decoded_payload['email'], self.email)

    def test_jwt_login_json_bad_creds(self):
        """
        Ensure JWT login view using JSON POST fails
        if bad credentials are used.
        """
        client = APIClient(enforce_csrf_checks=True)

        self.data['password'] = 'wrong'
        response = client.post('/api-auth/', self.data, format='json')

        self.assertEqual(response.status_code, 400)

    def test_jwt_login_json_missing_fields(self):
        """
        Ensure JWT login view using JSON POST fails if missing fields.
        """
        client = APIClient(enforce_csrf_checks=True)

        response = client.post('/api-auth/',
                               {'username': self.username}, format='json')

        self.assertEqual(response.status_code, 400)

    def test_jwt_login_form(self):
        """
        Ensure JWT login view using form POST works.
        """
        client = APIClient(enforce_csrf_checks=True)

        response = client.post('/api-auth/', self.data)

        decoded_payload = utils.jwt_decode_handler(response.data['token'])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(decoded_payload['email'], self.email)

    def test_jwt_login_with_expired_token(self):
        """
        Ensure JWT login view works even if expired token is provided
        """
        payload = utils.jwt_payload_handler(self.user)
        payload['exp'] = 1
        token = utils.jwt_encode_handler(payload)

        auth = 'JWT {0}'.format(token)
        client = APIClient(enforce_csrf_checks=True)
        response = client.post(
            '/api-auth/', self.data,
            HTTP_AUTHORIZATION=auth, format='json')

        decoded_payload = utils.jwt_decode_handler(response.data['token'])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(decoded_payload['email'], self.email)

    def test_jwt_login_using_zero(self):
        """
        Test to reproduce issue #33
        """
        client = APIClient(enforce_csrf_checks=True)

        data = {
            'username': '0',
            'password': '0'
        }

        response = client.post('/api-auth/', data, format='json')

        self.assertEqual(response.status_code, 400)



class TokenTestCase(BaseTestCase):
    """
    Handlers for getting tokens from the API, or creating arbitrary ones.
    """

    def setUp(self):
        super(TokenTestCase, self).setUp()

    def get_token(self):
        client = APIClient(enforce_csrf_checks=True)
        response = client.post('/api-auth/', self.data, format='json')
        return response.data['token']

    def create_token(self, user, exp=None, orig_iat=None):
        payload = utils.jwt_payload_handler(user)
        if exp:
            payload['exp'] = exp

        if orig_iat:
            payload['orig_iat'] = timegm(orig_iat.utctimetuple())

        token = utils.jwt_encode_handler(payload)
        return token


class RefreshJSONWebTokenTests(TokenTestCase):

    def setUp(self):
        super(RefreshJSONWebTokenTests, self).setUp()
        api_settings.JWT_ALLOW_REFRESH = True

    def test_refresh_jwt(self):
        """
        Test getting a refreshed token from original token works
        No date/time modifications are neccessary because it is assumed
        that this operation will take less than 300 seconds.
        """
        client = APIClient(enforce_csrf_checks=True)
        orig_token = self.get_token()
        orig_token_decoded = utils.jwt_decode_handler(orig_token)

        expected_orig_iat = timegm(datetime.utcnow().utctimetuple())

        # Make sure 'orig_iat' exists and is the current time (give some slack)
        orig_iat = orig_token_decoded['orig_iat']
        self.assertLessEqual(orig_iat - expected_orig_iat, 1)

        time.sleep(1)

        # Now try to get a refreshed token
        response = client.post('/auth-token-refresh/', {'token': orig_token},
                               format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        new_token = response.data['token']
        new_token_decoded = utils.jwt_decode_handler(new_token)

        # Make sure 'orig_iat' on the new token is same as original
        self.assertEquals(new_token_decoded['orig_iat'], orig_iat)
        self.assertGreater(new_token_decoded['exp'], orig_token_decoded['exp'])

    def test_refresh_jwt_after_refresh_expiration(self):
        """
        Test that token can't be refreshed after token refresh limit
        """
        client = APIClient(enforce_csrf_checks=True)

        orig_iat = (datetime.utcnow() - api_settings.JWT_REFRESH_EXPIRATION_DELTA -
                    timedelta(seconds=5))

        token = self.create_token(
            self.user,
            exp=datetime.utcnow() + timedelta(hours=1),
            orig_iat=orig_iat
        )

        response = client.post('/auth-token-refresh/', {'token': token},
                               format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0],
                         'Refresh has expired.')

    def tearDown(self):
        # Restore original settings
        api_settings.JWT_ALLOW_REFRESH = DEFAULTS['JWT_ALLOW_REFRESH']
