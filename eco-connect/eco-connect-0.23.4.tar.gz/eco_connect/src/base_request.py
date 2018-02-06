import requests

from eco_connect.src.errors import InvalidRequest
from eco_connect.src.request_parser import RequestParser
from eco_connect.src.credentials_factory import CredentialsFactory


class BaseRequest:

    def __init__(self):
        self._set_credentials()

    def _validate_env(self, environment_name):
        environment_name = environment_name.lower()
        valid_envs = ['prod', 'qa', 'dev']
        if environment_name in valid_envs:
            return environment_name
        else:
            raise ValueError(f'`{environment_name}` is invalid! Chose from '
                             f'{valid_envs}')

    def _set_credentials(self):
        self.credentials = CredentialsFactory.get_eco_credentials()

    def get(self, url, data={}):
        kwargs = self._format_kwargs(data=data,
                                     encode_type='querystring')
        return requests.get(url, **kwargs)

    def put(self, url, data={}, encode_type='form'):
        kwargs = self._format_kwargs(data=data,
                                     encode_type=encode_type)
        return requests.put(url, **kwargs)

    def post(self, url, data={}, files={}, encode_type='form'):
        kwargs = self._format_kwargs(data=data,
                                     files=files,
                                     encode_type=encode_type)
        return requests.post(url, **kwargs)

    def delete(self, url, data={}, encode_type='form'):
        kwargs = self._format_kwargs(data=data,
                                     encode_type=encode_type)
        return requests.delete(url, **kwargs)

    def _format_kwargs(self, data, encode_type, files={}):
        if encode_type.lower() == 'querystring':
            kw_dict = {'auth': self.credentials, 'params': data}
            return kw_dict

        elif encode_type.lower() == 'form':
            kw_dict = {'auth': self.credentials, 'data': data}
            if files:
                kw_dict.update({'files': files})
            return kw_dict

        elif encode_type.lower() == 'json':
            kw_dict = {'auth': self.credentials, 'json': data}
            return kw_dict

        else:
            raise ValueError(f'({encode_type}) is not valid!')

    def _format_response(self, response,
                         parser=RequestParser.json_parser,
                         parser_args={}):
        if response.status_code == 200 or response.status_code == 201:
            return parser(response, **parser_args)

        elif response.status_code == 401:
            print('Invalid credentials. Did you remeber to set you '
                  'environment variables?. '
                  'See `https://github.com/ecorithm/eco-connect/README.md` '
                  ' for more information.')
            raise InvalidRequest()

        else:
            try:
                return response.json()
            except ValueError:
                return response.text

    def _get_parser(self, result_format, data_key='data'):
        parser = {'parser': None, 'parser_args': {}}
        if result_format.lower() == 'pandas':
            parser['parser_args'] = {'data_key': data_key}
            parser['parser'] = RequestParser.pandas_parser
        elif result_format.lower() == 'json':
            parser['parser'] = RequestParser.json_parser
            parser['parser_args'] = {}
        elif result_format.lower() == 'tuple':
            parser['parser'] = RequestParser.tuple_parser
            parser['parser_args'] = {'data_key': data_key}
        elif result_format.lower() == 'csv':
            parser['parser'] = RequestParser.csv_parser
            parser['parser_args'] = {'data_key': data_key}
        else:
            raise ValueError(f'{result_format} is not valid!.'
                             ' Valid formats are (pandas, json, tuple, csv)')

        return parser
