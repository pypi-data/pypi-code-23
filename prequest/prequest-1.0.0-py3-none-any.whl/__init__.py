from .prequest import Prequest
from requests import Response
from typing import Dict

__version__ = '1.0.0'


def get(url: str, **kwargs) -> Response:
    """
    Sends a GET request.
    If the data is not available, it is returned from cache if possible.

    :param url: URL for the new Request object.
    :param kwargs: Optional arguments that request takes.
    :return: Response object
    :rtype: requests.Response
    """

    with Prequest() as pq:
        return pq.get(url, **kwargs)


def post(url: str, data: Dict = None, json: str = None, **kwargs) -> Response:
    """
    Sends a GET request.
    If the data is not available, it is returned from cache if possible.

    :param url: URL for the new Request object.
    :param data: (optional) Dictionary, bytes, or file-like object to send in the body of the Request.
    :param json: (optional) Json to send in the body of the Request.
    :param kwargs: Optional arguments that request takes.
    :return: Response object
    :rtype: requests.Response
    """

    with Prequest() as pq:
        return pq.post(url, data, json, **kwargs)


def put(url: str, data: Dict = None, **kwargs) -> Response:
    """
    Sends a PUT request.

    :param url: URL for the new Request object.
    :param data: (optional) Dictionary, bytes, or file-like object to send in the body of the Request.
    :param kwargs: Optional arguments that request takes.
    :return: Response object
    :rtype: requests.Response
    """

    with Prequest() as pq:
        return pq.put(url, data=data, **kwargs)


def delete(url: str, **kwargs) -> Response:
    """
    Sends a DELETE request.

    :param url: URL for the new Request object.
    :param kwargs: Optional arguments that request takes.
    :return: Response object
    :rtype: requests.Response
    """
    with Prequest() as pq:
        return pq.delete(url, **kwargs)
