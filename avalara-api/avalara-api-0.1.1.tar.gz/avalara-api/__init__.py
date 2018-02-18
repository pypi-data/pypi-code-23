import typing

from avalara-api.abstract_client import AbstractClient

def get_api_client(username: typing.AnyStr, password: typing.AnyStr, accountid: typing.AnyStr, is_prod) -> AvalaraClient:
    return AvalaraClient()
