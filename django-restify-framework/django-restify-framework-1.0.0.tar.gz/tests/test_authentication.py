from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.test import TestCase, RequestFactory

from restify.authentication import ApiKeyAuthentication, DjangoAuthentication
from restify.http import status
from restify.models import ApiKey
from restify.resource import Resource


class Resource1(Resource):
    class Meta:
        authentication = ApiKeyAuthentication

    def get(self, request, *args, **kwargs):
        return HttpResponse('')


class ApiAuthTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='user1', password='passwd1')

    def test_apikey_generated(self):
        self.assertEquals(ApiKey.objects.filter(user=self.user).count(), 1)

    def test_is_authenticated_get_params(self):
        auth = ApiKeyAuthentication()
        request = HttpRequest()
        request.method = 'GET'

        # No username/api_key details should fail.
        self.assertFalse(auth.is_authenticated(request))

        # Wrong username details.
        request.GET['username'] = 'foo'
        self.assertFalse(auth.is_authenticated(request))

        # No api_key.
        request.GET['username'] = self.user.username
        self.assertFalse(auth.is_authenticated(request))

        # Wrong user/api_key.
        request.GET['username'] = self.user.username
        request.GET['api_key'] = 'foo'
        self.assertFalse(auth.is_authenticated(request))

        # Correct user/api_key.
        request.GET['username'] = self.user.username
        request.GET['api_key'] = self.user.api_key.key
        self.assertTrue(auth.is_authenticated(request))

    def test_is_authenticated_header(self):
        auth = ApiKeyAuthentication()
        request = HttpRequest()
        request.method = 'GET'

        # Wrong username details.
        request.META['HTTP_AUTHORIZATION'] = 'foo'
        self.assertFalse(auth.is_authenticated(request))

        # No api_key.
        request.META['HTTP_AUTHORIZATION'] = 'ApiKey {0}'.format(self.user.username)
        self.assertFalse(auth.is_authenticated(request))

        # Wrong user/api_key.
        request.META['HTTP_AUTHORIZATION'] = 'ApiKey {0}:pass'.format(self.user.username)
        self.assertFalse(auth.is_authenticated(request))

        # Correct user/api_key.
        request.META['HTTP_AUTHORIZATION'] = 'ApiKey {0}:{1}'.format(self.user.username, self.user.api_key.key)
        self.assertTrue(auth.is_authenticated(request))

        # Capitalization shouldn't matter.
        request.META['HTTP_AUTHORIZATION'] = request.META['HTTP_AUTHORIZATION'].replace('ApiKey', 'aPikEy')
        self.assertTrue(auth.is_authenticated(request))

    def test_check_active_true(self):
        auth = ApiKeyAuthentication()
        request = HttpRequest()
        request.method = 'GET'

        self.user.is_active = False
        self.user.save()
        request.META['HTTP_AUTHORIZATION'] = 'ApiKey {0}:{1}'.format(self.user.username, self.user.api_key.key)
        self.assertFalse(auth.is_authenticated(request))

    def test_resource_auth(self):
        rf = RequestFactory()
        resource = Resource1.as_callable()

        request = rf.get('/')
        response = resource(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ResourceSession(Resource):
    class Meta:
        authentication = DjangoAuthentication

    def get(self, request, *args, **kwargs):
        return HttpResponse('')


class SessionAuthTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='user1', password='passwd1')

    def test_no_user_with_user(self):
        request = HttpRequest()
        auth = DjangoAuthentication()

        self.assertFalse(auth.is_authenticated(request))

        request.user = self.user
        self.assertTrue(auth.is_authenticated(request))

    def test_resource_auth(self):
        rf = RequestFactory()
        resource = ResourceSession.as_callable()

        request = rf.get('/')
        request.user = self.user
        response = resource(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)