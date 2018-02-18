import typing

from .avalara_client import AvalaraClient

def get_api_client(username: typing.AnyStr, password: typing.AnyStr, accountid: typing.AnyStr, is_prod) -> AvalaraClient:
    return AvalaraClient()
