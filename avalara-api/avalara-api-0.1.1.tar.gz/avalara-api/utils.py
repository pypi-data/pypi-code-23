import typing
import requests
import json

BodyOrDto = typing.Optional[typing.Union[dto.BaseDto, typing.Dict]]


class ResponseObject(object):
    def __init__(self, status_code, text, error_message=None):
        self.error_message = error_message
        self.status_code = status_code
        self.text = text


class RequestUtil(object):
    def __init__(self, client_id: str, user_id: str, endpoint: str):
        self.client_id = client_id
        self.user_id = user_id
        self.endpoint = endpoint if endpoint.endswith('/') else "{}/".format(endpoint)

    __GET = 'GET'
    __PUT = 'PUT'
    __POST = 'POST'
    __DELETE = 'DELETE'
    __AVAILABLE_HTTP_METHODS = [__GET, __PUT, __POST, __DELETE]
    __ERROR_DESCRIPTIONS = {
        400: 'Bad Request',
        404: 'Not Found',
        409: 'Conflict',
        401: 'Unauthorized',
        500: 'Internal Server Error',
        503: 'Service temporary unavailable'
    }

    def __make_request(self, method: typing.AnyStr, path: typing.AnyStr, query_params: typing.Dict = None,
                       headers: typing.Dict = None, dto_object=None, continuation_token=None) -> ResponseObject:

        assert method in self.__AVAILABLE_HTTP_METHODS, 'Http method should be one of [{}]. \'{}\' got.'.format(
            ",".join(['\'%s\'' % m for m in self.__AVAILABLE_HTTP_METHODS]), method)

        url = "{}{}".format(self.endpoint, path)
        json_body = json.dumps(dto_object.to_dict()) if dto_object else None
        real_headers = (headers or {}).copy()
      #  real_headers[defaults.CLIENT_ID_HEADER_NAME] = self.client_id
      #  real_headers[defaults.USER_ID_HEADER_NAME] = self.user_id
        real_headers['Content-Type'] = "application/json; charset=utf-8"
        real_headers['Accept'] = "application/json"
        real_query_params = (query_params or {}).copy()
        if continuation_token:
            real_query_params[defaults.CONTINUATION_TOKEN_NAME] = continuation_token
        response = requests.request(method=method,
                                    url=url,
                                    params=real_query_params,
                                    headers=real_headers,
                                    data=json_body)
        status_code = int(response.status_code)
        error_message = self.__ERROR_DESCRIPTIONS.get(status_code, None)
        return ResponseObject(status_code, response.text, error_message)

    def get(self, path: typing.AnyStr, query_params: typing.Dict = None, headers: typing.Dict = None,
            continuation_token=None) -> ResponseObject:
        return self.__make_request(self.__GET, path, query_params, headers, None, continuation_token=continuation_token)

    def post(self, path: typing.AnyStr, dto_obj: BodyOrDto, query_params: typing.Dict = None,
             headers: typing.Dict = None) -> ResponseObject:
        return self.__make_request(self.__POST, path, query_params, headers, dto_obj)

    def put(self, path: typing.AnyStr, dto_obj: BodyOrDto, query_params: typing.Dict = None,
            headers: typing.Dict = None) -> ResponseObject:
        return self.__make_request(self.__PUT, path, query_params, headers, dto_obj)

    def delete(self, path: typing.AnyStr, query_params: typing.Dict = None,
               headers: typing.Dict = None) -> ResponseObject:
        return self.__make_request(self.__DELETE, path, query_params, headers, None)
