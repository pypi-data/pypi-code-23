# coding: utf-8

import json
from typing import Dict

from requests import HTTPError, PreparedRequest, Request, Response, Session

from restify.task.client.auth import AuthBase


class ClientException(Exception):
    def __init__(self, response: Response):
        self.response = response


class UnexpectedFormatException(ClientException):
    """
    Raised when the remote backend returns an invalid JSON.
    """


class RemoteException(ClientException):
    """
    Raised when the remote function raises an exception.
    The object stores the text of the remote traceback.
    """

    def __init__(self, response: Response):
        super().__init__(response)

        try:
            self.exception = self.response.json()['exception']
        except Exception as e:
            raise UnexpectedFormatException(self.response)

    def __str__(self):
        return '\n"""\n{0}"""'.format(self.exception)


class Client:
    def __init__(self, api: str, auth: AuthBase, **requests_kwargs):
        requests_kwargs.setdefault('timeout', 10)

        self._api = api
        self._auth = auth
        self._requests_kwargs = requests_kwargs

        self._session = Session()

    def _prepare(self, signature: Dict) -> PreparedRequest:
        request = Request('POST', self._api, json=signature)

        self._auth.inject_credentials(request)

        return self._session.prepare_request(request)

    def _send(self, request: PreparedRequest) -> Response:
        return self._session.send(request, **self._requests_kwargs)

    def call(self, name, args=None, kwargs=None):
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}

        request = self._prepare({
            'function': name,
            'args': args,
            'kwargs': kwargs
        })

        response = self._send(request)

        try:
            response.raise_for_status()
            retval = response.json()

        except json.JSONDecodeError as e:
            raise UnexpectedFormatException(response)

        except HTTPError as e:
            if response.status_code == 400:
                raise RemoteException(response)
            else:
                raise
        else:
            try:
                return retval['return']
            except KeyError:
                raise UnexpectedFormatException(response)
