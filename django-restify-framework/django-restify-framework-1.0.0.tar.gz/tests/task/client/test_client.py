# coding: utf-8
from json import JSONDecodeError
from unittest.mock import call, patch, MagicMock

from django.test import TestCase
from requests import HTTPError

from restify.task.client import Client, ClientException, RemoteException, UnexpectedFormatException


class ClientExceptionTests(TestCase):
    def test_init(self):
        mock_response = MagicMock()

        e = ClientException(mock_response)
        self.assertIs(e.response, mock_response)


class UnexpectedFormatExceptionTests(TestCase):
    def test_init(self):
        self.assertTrue(issubclass(UnexpectedFormatException, ClientException))


class RemoteExceptionTests(TestCase):
    def test_init(self):
        mock_response = MagicMock(**{'json.return_value': None})

        self.assertRaises(UnexpectedFormatException, lambda: RemoteException(mock_response))

        mock_response.json.return_value = {
            'exception': 'EXCEPTION'
        }

        e = RemoteException(mock_response)
        self.assertEqual(e.exception, 'EXCEPTION')

        self.assertEqual(
            str(e),
            '\n'
            '"""\n'
            'EXCEPTION'  # Note: There is no explicit \n here
            '"""'
        )


class ClientTests(TestCase):
    @patch('restify.task.client.Client._send')
    @patch('restify.task.client.Client._prepare')
    def test_call(self, mock_prepare: MagicMock, mock_send: MagicMock):
        mock_send.return_value = MagicMock(**{'json.return_value': {'return': 'RETVAL'}})

        client = Client('api', None)
        retval = client.call('some_task', args=('arg0', ), kwargs={'kwarg0': 'value0'})

        self.assertEqual(retval, 'RETVAL')

        self.assertEqual(mock_prepare.mock_calls, [
            call({
                'function': 'some_task',
                'args': ('arg0', ),
                'kwargs': {'kwarg0': 'value0'}
            })
        ])

        self.assertEqual(mock_send.mock_calls, [
            call(mock_prepare.return_value),
            call().raise_for_status(),
            call().json()
        ])

    @patch('restify.task.client.Client._send')
    @patch('restify.task.client.Client._prepare')
    def test_call_json_decode_error(self, mock_prepare: MagicMock, mock_send: MagicMock):
        mock_send.return_value = MagicMock(**{'json.side_effect': JSONDecodeError('', '', 0)})

        client = Client('api', None)
        with self.assertRaises(UnexpectedFormatException) as e:
            client.call('some_task')

        self.assertEqual(e.exception.response, mock_send.return_value)

    @patch('restify.task.client.Client._send')
    @patch('restify.task.client.Client._prepare')
    def test_call_json_structure_error(self, mock_prepare: MagicMock, mock_send: MagicMock):
        mock_send.return_value = MagicMock(**{'json.return_value': {}})

        client = Client('api', None)
        with self.assertRaises(UnexpectedFormatException) as e:
            client.call('some_task')

        self.assertEqual(e.exception.response, mock_send.return_value)

    @patch('restify.task.client.Client._send')
    @patch('restify.task.client.Client._prepare')
    def test_call_http_error(self, mock_prepare: MagicMock, mock_send: MagicMock):
        mock_send.return_value = MagicMock(**{
            'raise_for_status.side_effect': HTTPError,
            'status_code': 400
        })

        client = Client('api', None)
        with self.assertRaises(RemoteException) as e:
            client.call('some_task')

        self.assertEqual(e.exception.response, mock_send.return_value)

    @patch('restify.task.client.Client._send')
    @patch('restify.task.client.Client._prepare')
    def test_call_server_error(self, mock_prepare: MagicMock, mock_send: MagicMock):
        mock_send.return_value = MagicMock(**{
            'raise_for_status.side_effect': HTTPError,
            'status_code': 500
        })

        client = Client('api', None)
        with self.assertRaises(HTTPError) as e:
            client.call('some_task')

    @patch('restify.task.client.Session')
    def test_prepare(self, mock_session: MagicMock):
        url = 'api'
        json = {'key': 'value'}

        mock_session = mock_session.return_value
        mock_auth = MagicMock()

        client = Client(url, mock_auth)
        self.assertEqual(client._prepare(json), mock_session.prepare_request.return_value)

        (name, (request, ), kwargs), = mock_auth.inject_credentials.mock_calls

        self.assertEqual(request.method, 'POST')
        self.assertEqual(request.url, url)
        self.assertEqual(request.json, json)

    @patch('restify.task.client.Session')
    def test_send(self, mock_session: MagicMock):
        mock_session = mock_session.return_value

        client = Client('api', None, verify=False)
        retval = client._send('REQUEST')

        self.assertEqual(mock_session.mock_calls, [
            call.send('REQUEST', timeout=10, verify=False)  # Note: timeout is an implicit default
        ])

        self.assertEqual(retval, mock_session.send.return_value)
