import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from yandex_checkout.configuration import Configuration
from yandex_checkout.domain.common.request_object import RequestObject
from yandex_checkout.domain.exceptions.api_error import ApiError
from yandex_checkout.domain.exceptions.bad_request_error import BadRequestError
from yandex_checkout.domain.exceptions.forbidden_error import ForbiddenError
from yandex_checkout.domain.exceptions.not_found_error import NotFoundError
from yandex_checkout.domain.exceptions.response_processing_error import ResponseProcessingError
from yandex_checkout.domain.exceptions.too_many_request_error import TooManyRequestsError
from yandex_checkout.domain.exceptions.unauthorized_error import UnauthorizedError


class ApiClient:
    endpoint = Configuration.api_endpoint()

    def __init__(self):
        self.configuration = Configuration.instantiate()
        self.shop_id = self.configuration.account_id
        self.shop_password = self.configuration.secret_key
        self.timeout = self.configuration.timeout
        self.max_attempts = self.configuration.max_attempts

    def request(self, method="", path="", query_params=None, headers=None, body=None):
        if isinstance(body, RequestObject):
            body.validate()
            body = dict(body)

        request_headers = self.prepare_request_headers(headers)
        raw_response = self.execute(body, method, path, query_params, request_headers)

        if raw_response.status_code != 200:
            self.__handle_error(raw_response)

        return raw_response.json()

    def execute(self, body, method, path, query_params, request_headers):
        session = self.get_session()
        raw_response = session.request(method,
                                       self.endpoint + path,
                                       params=query_params,
                                       headers=request_headers,
                                       json=body,
                                       auth=(self.shop_id, self.shop_password))
        return raw_response

    def get_session(self):
        session = requests.Session()
        retries = Retry(total=self.max_attempts,
                        backoff_factor=self.timeout / 1000,
                        method_whitelist=['POST'],
                        status_forcelist=[202])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        return session

    def prepare_request_headers(self, headers):
        request_headers = {'Content-type': 'application/json'}
        if isinstance(headers, dict):
            request_headers.update(headers)
        return request_headers

    def __handle_error(self, raw_response):
        http_code = raw_response.status_code
        if http_code == BadRequestError.HTTP_CODE:
            raise BadRequestError(raw_response.json())
        elif http_code == ForbiddenError.HTTP_CODE:
            raise ForbiddenError(raw_response.json())
        elif http_code == NotFoundError.HTTP_CODE:
            raise NotFoundError(raw_response.json())
        elif http_code == TooManyRequestsError.HTTP_CODE:
            raise TooManyRequestsError(raw_response.json())
        elif http_code == UnauthorizedError.HTTP_CODE:
            raise UnauthorizedError(raw_response.json())
        elif http_code == ResponseProcessingError.HTTP_CODE:
            raise ResponseProcessingError(raw_response.json())
        else:
            raise ApiError(raw_response.text)
