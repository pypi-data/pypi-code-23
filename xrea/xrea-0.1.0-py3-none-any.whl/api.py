from .error import XreaApiResponseError
import requests


class ApiCall:
    def __init__(self, api_parts, func):
        self.api_parts = api_parts
        self.func = func

    def __getattr__(self, item):
        self.api_parts.append(item)
        return self

    def __call__(self, *args, **kwargs):
        api = '/'.join(self.api_parts)
        return self.func(api, **kwargs)


class ApiResponse:
    def __init__(self, api_url, **kwargs):
        self.api_url = api_url
        self.params = kwargs
        self.raw_response = requests.post(api_url, kwargs)
        self.json = self.raw_response.json()
        if not (self.is_success and self.is_http_ok):
            raise XreaApiResponseError(self)

    @property
    def message(self):
        return self.json.get('message')

    @property
    def result(self):
        return self.json.get('result')

    @property
    def status_code(self):
        return self.json.get('status_code')

    @property
    def is_success(self):
        return self.status_code == 200

    @property
    def http_status_code(self):
        return self.raw_response.status_code

    @property
    def is_http_ok(self):
        return self.http_status_code == requests.codes.ok


class ApiBase:
    def __init__(self, *, base_url, api_version='v1',
                 account, server_name, api_secret_key):
        self.base_url = base_url
        self.api_version = api_version
        self.account = account
        self.server_name = server_name
        self.api_secret_key = api_secret_key

    def call_api(self, api, **kwargs):
        api_url = '/'.join([self.base_url, self.api_version, api])
        kwargs.update(self.api_user_params)
        return ApiResponse(api_url, **kwargs)

    def __getattr__(self, k):
        return ApiCall(api_parts=[k], func=self.call_api)

    @property
    def api_user_params(self):
        return {
            'account': self.account,
            'server_name': self.server_name,
            'api_secret_key': self.api_secret_key,
        }
