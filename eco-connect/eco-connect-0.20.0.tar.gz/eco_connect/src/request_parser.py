import os
from collections import namedtuple

import pandas as pd

from eco_connect.src.errors import RequestParserError


class RequestParser:

    @classmethod
    def json_parser(cls, response):
        try:
            return response.json()
        except ValueError:
            return response.text

    @classmethod
    def tuple_parser(cls, response, data_key=None):
        try:
            result = response.json()
        except ValueError:
            raise RequestParserError('Unable to parse the response.',
                                     response.text)

        try:
            if data_key:
                result = result[data_key]
        except KeyError:
            raise RequestParserError('Unable to parse the response.',
                                     result)

        parsed_result = []

        if isinstance(result, dict):
            response_tuple = namedtuple('response_tuple', result.keys())
            return [response_tuple(**result)]

        elif isinstance(result, list) and isinstance(result[0], dict):
            response_tuple = namedtuple('response_tuple', result[0].keys())
            for row in result:
                parsed_result.append(response_tuple(**row))
            return parsed_result

        else:
            raise RequestParserError('Unable to parse the response.')

    @classmethod
    def pandas_parser(cls, response, data_key=None):
        tuple_response = cls.tuple_parser(response, data_key)
        return pd.DataFrame(tuple_response)

    @classmethod
    def csv_parser(cls, response,
                   data_key=None):
        result_df = cls.pandas_parser(response, data_key=data_key)
        return result_df.to_csv()
