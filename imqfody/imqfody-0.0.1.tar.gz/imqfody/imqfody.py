import requests
import json

from requests.auth import HTTPBasicAuth


class FodyError(Exception):
    pass


class UnknownHandler(FodyError):
    pass


class HTTPError(FodyError):
    pass


class IMQFody(object):
    def __init__(self, url, username, password):
        object.__init__(self)
        self._url = url.rstrip('/')
        self._session = requests.session()
        self._session.auth = HTTPBasicAuth(username, password)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()

    def _search(self, handler, endpoint, query):
        """Generic search method to build queries.

        :param handler: Handler on fody side: [contactdb, events, tickets, checkticket]
        :param endpoint: Specific endpoint; e.g. searchasn, searchorg etc.
        :param query: Input used for querying fody."""
        if handler not in ['contactdb', 'events', 'tickets', 'checkticket']:
            raise UnknownHandler('Handler must be one of [contactdb, events, tickets, checkticket].')
        response = self._session.get('{}/api/{}/{}'.format(self._url, handler, endpoint), data=query)
        if response.status_code != 200:
            raise HTTPError(response.status_code)
        dict_response = json.loads(response.text)
        response.close()
        return dict_response

    def get_api_documentation(self):
        """Querying the base url returns the documentation"""
        return json.loads(self._session.get(self._url))

    # ContactDB queries
    def ping(self):
        return self._search('contactdb', 'ping', {})
