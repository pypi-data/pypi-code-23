import inspect
import requests
try:
    from exceptions import SingularException
    from singular_api.settings import(
            ENDPOINTS,
            SINGULAR_URL,
            )
except ModuleNotFoundError:
    from .exceptions import SingularException
    from .settings import (
            ENDPOINTS,
            SINGULAR_URL,
            )


# TODO add arguments descriptions in function doctrings

def myself():
    """Returns name of function that is one step above in stack"""
    return inspect.stack()[1][3]


class Client:
    """Singular API client class. Provides methods to call Singular API from python scripts."""
    # TODO do we need appname here?
    def __init__(self, singular_token=None, singular_url=SINGULAR_URL, connect_timeout=5, read_timeout=5):
        """Basic Client init method

Keyword arguments:
singular_token (optional) -- OAuth2 Singular API token
singular_url (optional) -- defines Singular API URL. Uses default if not provided. Example - 'http://localhost:8000'.
connect_timeout (optional) -- connect timeout (see Requests module)
read_timeout (optional) -- read timeout (see Requests module)"""
        self._singular_url = singular_url
        self._singular_token = singular_token
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout

    def set_singular_token(self, token):
        """Sets Singular Token, which will be used to make every subsequest calls to Singular API"""
        self._singular_token = token

    def ping(self):
        """Tests connection to Singular API"""
        response, status_code = self._call_singular(ENDPOINTS[myself()]['url'], ENDPOINTS[myself()]['method'])
        connection_status = response.get('ping') == 'pong'
        return connection_status, status_code

    def schedule(self, start_time, end_time):
        endpoint = 'api/schedule/'
        data = {
                'start_time' : start_time,
                'end_time': end_time,
                }
        self._call_singular(endpoint, 'POST', json_body=data)

    def user_data(self):
        endpoint = 'api/user_data/'
        self._call_singular(endpoint, 'GET')

    def _call_singular(self, url, method, params=None, json_body=None, encoded_body=None, request_headers=None):
        """Makes actual Singular API requests

Keyword arguments:
endpoind -- Singular API endpoint dictionary, containing URL and HTTP request method. See settings.py.
params (optional) -- URL parameters dictionary
json_body (optional) -- json which should be sent in HTTP POST request body
encoded_body (optional) -- URL encoded data which should be sent in HTTP POST request body. Used only when json_body is None
request_headers (optional) -- HTTP request headers"""
        url = self._singular_url + url

        if self._singular_token is not None:
            headers = {
                'Authorization': 'Bearer {}'.format(self._singular_token)
            }
        else:
            headers = {}

        if request_headers is not None:
            headers.update(request_headers)
        timeouts = (self.connect_timeout, self.read_timeout)
        try:
            if json_body is not None:
                headers['Content-Type'] = 'application/json'
                response = requests.request(method, url, json=json_body, headers=headers, params=params, timeout=timeouts)
            elif encoded_body is not None:
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
                response = requests.request(method, url, data=encoded_body, headers=headers, params=params, timeout=timeouts)
            else:
                response = requests.request(method, url, headers=headers, params=params, timeout=timeouts)

            if response.status_code in [200, 201, 202]:
                return response.json(), response.status_code
            else:
                raise SingularException.from_response(response.status_code, response.text)

        except requests.exceptions.ConnectTimeout:
            raise SingularException.from_response(504, 'Connection timeout')
        except requests.exceptions.ReadTimeout:
            raise SingularException.from_response(504, 'Read timeout')
        except requests.exceptions.ConnectionError:
            raise SingularException.from_response(502, 'Connection error')

