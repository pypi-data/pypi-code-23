import requests

from mailtest.errors import MailTestError


class Client(object):
    """
    MailTest Client

    HTTP connections to and communication with the MailTest API.
    """

    def __init__(self, api, **kwargs):
        self._api = api

    def _request(self, url, method, params=None, data=None, **kwargs):
        url = "%s/%s" % (self._api.base_url, url)
        headers = kwargs.pop("headers", {})

        try:
            response = requests.request(method, url, params=params, data=data, headers=headers, **kwargs)
        except Exception as e:
            raise MailTestError("Connection error: %s" % e)

        try:
            result = response.json()
        except ValueError as e:
            raise MailTestError
        return result

    def _get(self, url, params=None, **kwargs):
        return self._request(url, "get", params=params, **kwargs)
