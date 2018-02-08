from django.contrib.auth.models import User as django_user
from rest_framework import status, exceptions
from rest_framework.test import APITestCase
from gcb_web_auth.dukeds_auth import DukeDSTokenAuthentication
from gcb_web_auth.models import DukeDSAPIToken
from mock.mock import patch, MagicMock


class ResponseStatusCodeTestCase(object):
    def assertUnauthorized(self, response):
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED,
                         'Got {}, expected 401 when authentication fails'
                         .format(response.status_code))

    def assertForbidden(self, response):
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN,
                         'Got {}, expected 403 when additional access required'
                         .format(response.status_code))


class DukeDSTokenAuthenticationClientTestCase(APITestCase, ResponseStatusCodeTestCase):

    def setUp(self):
        self.user = django_user.objects.create_user('user1', is_staff=True)
        self.token_auth = DukeDSTokenAuthentication()

    @staticmethod
    def create_request(token):
        request = MagicMock()
        request.META = {
            'HTTP_X_DUKEDS_AUTHORIZATION': token
        }
        return request

    @patch('gcb_web_auth.backends.dukeds.check_jwt_token')
    def test_active_user(self, mock_check_jwt_token):
        token = DukeDSAPIToken.objects.create(user=self.user, key='2mma0c3')
        request = self.create_request(token.key)
        result = self.token_auth.authenticate(request)
        self.assertIsNotNone(result)
        result_user, result_token = result
        self.assertEqual('2mma0c3', result_token.key)
        self.assertEqual(self.user, result_user)
        self.assertTrue(mock_check_jwt_token.called_with(token.key))

    def test_with_invalid_jwt(self):
        DukeDSAPIToken.objects.create(user=self.user, key='2mma0c3')
        request = self.create_request('abacaa')  # Not a valid JWT
        with self.assertRaises(exceptions.AuthenticationFailed) as re:
            self.token_auth.authenticate(request)
        self.assertEqual('Invalid token.', str(re.exception))

    def test_no_token(self):
        request = MagicMock()
        request.META = {
            'HTTP_X_DUKEDS_AUTHORIZATION': ''
        }
        with self.assertRaises(exceptions.AuthenticationFailed) as re:
            self.token_auth.authenticate(request)
        self.assertEqual('Invalid token header. No credentials provided.', str(re.exception))

    @patch('gcb_web_auth.backends.dukeds.check_jwt_token')
    def test_inactive_user(self, mock_check_jwt_token):
        self.user.is_active = False
        self.user.save()
        token = DukeDSAPIToken.objects.create(user=self.user, key='2mma0c3')
        request = self.create_request(token.key)
        with self.assertRaises(exceptions.AuthenticationFailed) as re:
            self.token_auth.authenticate(request)
        self.assertEqual('User inactive or deleted.', str(re.exception))
