from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import TestCase, RequestFactory

from restify.authorization import DjangoPermissions
from restify.http import status
from restify.resource import Resource


class Resource1(Resource):
    class Meta:
        authorization = DjangoPermissions(get='app.permission')

    def get(self, request, *args, **kwargs):
        return HttpResponse('')

    def post(self, request, *args, **kwargs):
        return HttpResponse('')


class DjangoAuthorizationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='user1')

    def test_has_perm(self):
        auth = DjangoPermissions(get='app.permission', post='app2.perm')

        self.assertFalse(auth.has_perm(self.user, http_method='get'))

        self.user.is_superuser = True
        self.assertTrue(auth.has_perm(self.user, http_method='get'))

    def test_authorization_without_authentication(self):
        rf = RequestFactory()
        resource = Resource1.as_callable()

        request = rf.get('/')
        response = resource(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_django_permissions(self):
        rf = RequestFactory()
        resource = Resource1.as_callable()

        request = rf.get('/')
        request.user = self.user
        response = resource(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        request = rf.post('/')
        request.user = self.user
        response = resource(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)