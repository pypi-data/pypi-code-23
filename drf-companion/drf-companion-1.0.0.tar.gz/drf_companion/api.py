import os, configparser, requests, json, http, logging, time, datetime
from functools import wraps

from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

SECRETS_LOCATION = os.environ.get('INTERFACE_CONF_FILE')
SECRETS_LOCATION = os.path.abspath(SECRETS_LOCATION)

config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config['DEFAULT'] = {
    "username": "username",
    "password": "password",
    "root_url": "http://localhost:8000",
    "api_uri": "api",
    "api_login_uri": "api/auth/login",
    "log_location": "",
}

config.read(SECRETS_LOCATION)


USERNAME = config.get('drf_companion', 'username')
PASSWORD = config.get('drf_companion', 'password')
ROOT_URL = config.get('drf_companion', 'root_url')
API_URI = config.get('drf_companion', 'api_uri')
API_LOGIN_URI = config.get('drf_companion', 'api_login_uri')
LOG_LOCATION = config.get('drf_companion', 'log_location')

# SETUP LOGGING
if LOG_LOCATION:
    logging.basicConfig(filename=os.path.abspath(LOG_LOCATION), filemode='w', level=logging.INFO)

# SETUP REQUESTS TIMNEOUT RETRIES
s = requests.Session()

retries = Retry(total=5,
                backoff_factor=0.1,
                status_forcelist=[ 500, 502, 503, 504])

s.mount(ROOT_URL, HTTPAdapter(max_retries=retries))

class ConnectionError(BaseException):
    pass


class APICallError(BaseException):
    pass

def handle_response(method):
    @wraps(method)
    def response_wrapper(self, *method_args, **method_kwargs):
        response = method(self, *method_args, **method_kwargs)
        if method_args:
            entity = method_args[0]
        else:
            entity = method_kwargs.get('entity')
        error, caller, entity_id, url = method_kwargs.pop('error', None), method.__name__, method_kwargs.pop('entity_id', None), method_kwargs.pop('url', None)
        _kwargs = method_kwargs
        if response.status_code >= 400:
            logging.error(f'[{datetime.datetime.now().isoformat()}] {url if url else ""} {self.username} '
                          f'{" passive fail " if not error else ""}{caller} {entity}'
                          f' {response.status_code} {response.text if hasattr(response, "text") else ""} {_kwargs}')
        elif self.logging:
            logging.info(
                f'[{datetime.datetime.now().isoformat()}] {url if url else ""} {self.username} {caller} {entity}'
                f' {response.status_code} {response.text if hasattr(response, "text") else ""} {_kwargs}')
        if response.status_code == 200:
            return json.loads(response.text)
        elif response.status_code == 201:
            return json.loads(response.text)
        elif response.status_code == 204:
            return {f"Success {response.status_code}": "Record deleted successfully."}
        elif str(response.status_code).startswith('2'):
            return {f"Success {response.status_code}": http.client.resonses[response.status_code]}
        elif str(response.status_code).startswith('3'):
            return {f"Redirection {response.status_code}": http.client.resonses[response.status_code]}
        elif response.status_code == 403:
            if not error:
                return {f"Error {response.status_code}": "Malformed request."}
            else:
                raise APICallError(f"Error {response.status_code}: Malformed request.")
        elif response.status_code == 404:
            if not error:
                return {f"Error {response.status_code}": "Record did not exist or non-existent endpoint."}
            else:
                raise APICallError(f"Error {response.status_code}: Record did not exist or non-existent endpoint.")
        elif response.status_code == 500:
            if not error:
                return {f"Error {response.status_code}": "Unspecified Error"}
            else:
                raise APICallError(f"Error {response.status_code}: Unspecified Error")
        else:
            if not error:
                return {f"Error {response.status_code}": response.text}
            else:
                raise APICallError(f"Error {response.status_code}: response.text")
    return response_wrapper


def prepare_request(method):
    @wraps(method)
    def request_wrapper(self, *method_args, **method_kwargs):
        if time.time() > self.token_details['expiry']:
            self._authenticate()
        if method_args:
            entity = method_args[0]
            if entity and issubclass(entity.__class__, str) and not entity.endswith('s'):
                entity += 's'
            elif entity is None:
                raise APICallError('entity must be passed')
        elif method.__name__ == 'entity_info':
            return method(self, **method_kwargs)
        else:
            raise APICallError('The first argument of this method must be the desired API entity.')
        if issubclass(entity.__class__, str):
            entity = entity.lower()
        return method(self, entity, *method_args[1:], **method_kwargs)
    return request_wrapper


class Interface:
    endpoint = f'{ROOT_URL}/{API_URI}'
    auth_endpoint = f'{ROOT_URL}/{API_LOGIN_URI}/'
    username = USERNAME
    password = PASSWORD

    def __init__(self, logging=False, global_timeout=10, **kwargs):
        # allows user to set custom endpoint and login creds
        for key, value in kwargs.items():
            if (key in ['endpoint', 'username', 'password']) and not value:
                kwargs[key] = self.__getattribute__(key)
        self.logging = logging
        self.global_timeout = global_timeout
        self._authenticate()

    def _authenticate(self):
        params = {"username": self.username, "password": self.password}
        response = s.post(f'{self.auth_endpoint}', timeout=self.global_timeout, auth=requests.auth.HTTPBasicAuth(**params))
        response_dict = json.loads(response.text)
        if 'token' not in response_dict.keys():
            raise ConnectionError('Could not establish a connection to the API. Please check your credentials.')
        self.token_details = response_dict
        self.token_details.update({'expiry': time.time() + 45 * 60})
        self.auth_token = response_dict['token']
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Token {self.auth_token}'
        }

    @prepare_request
    @handle_response
    def all(self, entity, error=False):
        request_kwargs = {"headers": self.headers}
        url = f'{self.endpoint}/{entity}/'
        response = s.get(url, timeout=self.global_timeout, **request_kwargs)
        return response

    @prepare_request
    @handle_response
    def search(self, entity, term, error=False):
        if not term:
            raise APICallError('Search term must be specified.')
        request_kwargs = {"headers": self.headers, "params": {"search": term}}
        url = f'{self.endpoint}/{entity}?'
        response = s.get(url, timeout=self.global_timeout, **request_kwargs)
        # response_dict = json.loads(response.text)
        # response = self._handle_status_code(response, caller='search', entity=entity, url=url, _kwargs={"term": term})
        return response

    @prepare_request
    @handle_response
    def query(self, entity=None, url=None, error=False, **kwargs):
        request_kwargs = {"headers": self.headers, "params": kwargs}
        if url:
            response = s.get(url, timeout=self.global_timeout, **request_kwargs)
        elif entity and kwargs:
            # raise NotImplementedError('Querying by entity values will be implemented if it is requested.')
            url = f'{self.endpoint}/{entity}?'
            response = s.get(url, timeout=self.global_timeout, **request_kwargs)
        else:
            raise APICallError('entity and Query terms must be specified.')
        return response

    @handle_response
    def page(self, paginated_response, error=False, page='next'):
        request_kwargs = {"headers": self.headers}
        if page in list(paginated_response.keys()) and paginated_response[page]:
            url = paginated_response[page]
        else:
            return False
        response = s.get(url, timeout=self.global_timeout, **request_kwargs)
        return response

    def de_paginate(self, paginated_response):
        pages, count = [], 0
        if 'results' not in list(paginated_response.keys()) or 'count' not in list(paginated_response.keys()):
            if issubclass(paginated_response.__class__, dict):
                pages.extend(paginated_response)
            else:
                raise APICallError('This is not a properly paginated response.')
        if 'results' in list(paginated_response.keys()):
            pages.extend(paginated_response['results'])
        if 'count' in list(paginated_response.keys()):
            count = paginated_response['count']
        next_page = paginated_response
        while len(pages) < count:
            next_page = self.page(next_page)
            if next_page:
                if 'results' in list(next_page.keys()):
                    pages.extend(next_page['results'])
            else:
                if len(pages) != len(count):
                    raise APICallError('Something went wrong during de-pagination; the number of de-paginated results '
                                       'was less than the expected number of results. Be sure that you always start '
                                       'de_page at the FIRST page of any paginated query results.')

        return pages

    @prepare_request
    @handle_response
    def add(self, entity, error=False, **kwargs):
        request_kwargs = {"headers": self.headers, "data": json.dumps(kwargs)}
        response = s.post(f'{self.endpoint}/{entity}/', timeout=self.global_timeout, **request_kwargs)
        return response

    def get_or_error(self, entity=None, url=None, **kwargs):
        response = self.query(entity, url=url,  **kwargs)
        if 'count' in response.keys() and response['count'] != 1:
            query_summary = '\n'.join([f'"{key}": "{value}"' for key, value in kwargs.items()])
            query_summary = f'({entity}={{{query_summary}}})'
            raise APICallError(f'{response["count"]} records match {query_summary}. Exactly 1 required for get request.')
        elif 'count' in response.keys() and response['count'] == 1:
            return response['results']
        elif not 'count' in response.keys():
            return response
        else:
            raise APICallError(f'An unknown error occurred during the handling of the get_or_error response: {response}.')

    def get_or_create(self, entity=None, **kwargs):
        response = self.query(entity, **kwargs)
        if 'count' in response.keys() and response['count'] > 1:
            raise APICallError(f'{len(response)} records match the provided query. Exactly 1 required for get request.')
        elif 'count' not in response.keys() or response['count'] == 0:
            response, created = self.add(entity, **kwargs), True
        else:
            response, created = response['results'][0], False

        return response, created

    @prepare_request
    @handle_response
    def add_file(self, entity=None, file=None, _file_field="file", error=False, **kwargs):
        with open(file, 'rb') as f:
            files = {_file_field: f}
            headers = {**self.headers}
            headers.pop('Content-Type')
            request_kwargs = {"headers": headers, "files": files, "data": kwargs}
            response = s.post(f'{self.endpoint}/{entity}/', timeout=self.global_timeout, **request_kwargs)
        return response

    @prepare_request
    @handle_response
    def edit(self, entity=None, entity_id=None, url=None, error=False, **kwargs):
        request_kwargs = {"headers": self.headers, "data": json.dumps(kwargs)}
        if url:
            response = s.patch(url, timeout=self.global_timeout, **request_kwargs)
        elif entity and entity_id:
            url = f'{self.endpoint}/{entity}/{entity_id}/'
            response = s.patch(url, timeout=self.global_timeout, **request_kwargs)
        else:
            raise APICallError('entity and entity_id or fully qualified url to resource must be provided.')
        return response

    @prepare_request
    @handle_response
    def delete(self, entity=None, entity_id=None, url=None, error=False, **kwargs):
        request_kwargs = {"headers": self.headers, "data": json.dumps(kwargs)}
        if url:
            response = s.delete(url, timeout=self.global_timeout, **request_kwargs)
        elif entity and entity_id:
            url = f'{self.endpoint}/{entity}/{entity_id}'
            response = s.delete(url, timeout=self.global_timeout, **request_kwargs)
        else:
            raise APICallError('entity and entity_id or fully qualified url to resource must be provided.')
        return response

    @prepare_request
    @handle_response
    def entity_info(self, entity=None, error=False, **kwargs):
        request_kwargs = {"headers": self.headers,}
        uri = f'{self.endpoint}/{entity}/' if entity else f'{self.endpoint}/'
        if not entity:
            # get will just list all of the stuff on root
            method = s.get
        else:
            # options will show everything you can do with the endpoint
            method = s.options
        response = method(uri, timeout=self.global_timeout, **request_kwargs)
        return response