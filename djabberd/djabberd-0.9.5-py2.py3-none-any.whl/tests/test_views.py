from unittest import mock

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase

from djabberd import views

from . import handlers as mock_handlers


factory = APIRequestFactory()


class AuthViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("djabberd:auth")
        self.args = '?username={}&password={}'

    def test_username_missing(self):
        url = self.url + self.args.format('username', '')
        request = factory.get(url)

        response = views.AuthView().as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_password_missing(self):
        url = self.url + self.args.format('', 'password')
        request = factory.get(url)

        response = views.AuthView().as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # To make testing easy setting use `username` to control the
    # result of `user_authentication`

    def test_http_200(self):
        url = self.url + self.args.format('True', 'password')
        request = factory.get(url)

        response = views.AuthView().as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_http_401(self):
        url = self.url + self.args.format('False', 'password')
        request = factory.get(url)

        response = views.AuthView().as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("djabberd:user")
        self.args = '?username={}'

    def test_username_missing(self):
        url = self.url + self.args.format('')
        request = factory.get(url)

        response = views.UserView().as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # To make testing easy setting use `username` to control the
    # result of `user_authentication`

    def test_user_exist(self):
        url = self.url + self.args.format('True')
        request = factory.get(url)

        response = views.UserView().as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_does_not_exist(self):
        url = self.url + self.args.format('False')
        request = factory.get(url)

        response = views.UserView().as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RosterViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("djabberd:roster")
        self.args = '?username={}'

    def test_username_missing(self):
        url = self.url + self.args.format('')
        request = factory.get(url)

        response = views.RosterView().as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_exist(self):
        url = self.url + self.args.format('True')
        request = factory.get(url)

        response = views.RosterView().as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, mock_handlers.TEST_ROSTER)

    def test_user_does_not_exist(self):
        url = self.url + self.args.format('False')
        request = factory.get(url)

        response = views.RosterView().as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ArchivePostViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("djabberd:archive")

    def test_http_200(self):
        data = mock_handlers.TEST_ARCHIVE
        request = factory.post(self.url, data=data, format='json')

        with mock.patch('djabberd.handlers.archive_store') as mock_handler:
            response = views.ArchiveView().as_view()(request)
            mock_handler.assert_called_with(data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ArchiveGetViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("djabberd:archive")
        self.args = '?username={}'

    def test_username_missing(self):
        url = self.url + self.args.format('')
        request = factory.get(url)

        response = views.ArchiveView().as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_with_username(self):
        username = 'True'
        url = self.url + self.args.format(username)
        request = factory.get(url)

        with mock.patch('djabberd.handlers.archive_get', autospec=True) as mh:
            mh.return_value = mock_handlers.TEST_ARCHIVE_GET
            response = views.ArchiveView().as_view()(request)
            mh.assert_called_with(username)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, mock_handlers.TEST_ARCHIVE_GET)

    def test_other_args_used(self):
        args = 'peer', 'after', 'before', 'limit', 'chat_type'
        username = 'True'
        for arg in args:
            url = self.url + self.args.format(username) + '&' + arg + '=asdf'
            self._test_arg(url, username, arg)

    def _test_arg(self, url, username, arg):
        with mock.patch('djabberd.handlers.archive_get', autospec=True) as mh:
            request = factory.get(url)
            views.ArchiveView().as_view()(request)
            mh.assert_called_with(username, **{arg: 'asdf'})
