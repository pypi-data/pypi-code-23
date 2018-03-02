from json import loads

import requests

from blueforge.core.exceptions import ParameterValidateError, UnknownServiceError
from blueforge.util import file


class Api(object):
    def __init__(self, service_name, raw_json=None):
        if raw_json is None:
            self.__raw_json = file.get_latest_api_json_file(service_name)
        else:
            self.__raw_json = raw_json

        if self.__raw_json:
            for method in self.__raw_json['api']:
                Api.__create_dynamic_method(self.__raw_json['meta']['endpoint'], method)
        else:
            raise UnknownServiceError('The {} service does not exist.'.format(service_name))

    @classmethod
    def __create_dynamic_method(cls, endpoint, method_obj):
        def request_http(self, *args, **kwargs):
            method = method_obj['method']
            url = (endpoint + method_obj['uri']).format(*args)
            params = {}
            for param in method_obj['params']:
                if param['name'] in kwargs:
                    params[param['name']] = kwargs[param['name']]
                elif param['require'] is not None and param['require'] is True:
                    raise ParameterValidateError('The parameter of {} is not defined.'.format(param['name']))

            # TODO: params와 json 구분 -> api.json에서 해야할듯
            if method == 'PUT':
                resp = requests.put(url=url, json=params, timeout=60)
            elif method == 'POST':
                resp = requests.post(url=url, params=params, timeout=60)
            elif method == 'DELETE':
                resp = requests.delete(url=url, params=params, timeout=60)
            else:
                resp = requests.get(url=url, params=params, timeout=60)

            return loads(resp.text)

        request_http.__name__ = method_obj['name']
        request_http.__doc__ = method_obj['description']
        setattr(cls, request_http.__name__, request_http)
