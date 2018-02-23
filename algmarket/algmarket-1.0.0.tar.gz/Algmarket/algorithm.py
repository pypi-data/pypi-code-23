'Algorithmia Algorithm API Client (python)'

import base64
import re
from Algmarket.async_response import AsyncResponse
from Algmarket.algm_response import AlgmResponse
from Algmarket.errors import ApiError, ApiInternalError
from enum import Enum

OutputType = Enum('OutputType','default raw void')

class Algorithm(object):
    def __init__(self, client, algoRef):
        # Parse algoRef
        algoRegex = re.compile(r"(?:algm://|/|)(\w+/.+)")
        m = algoRegex.match(algoRef)
        if m is not None:
            self.client = client
            self.path = m.group(1)
            self.url = '/v1/algm/' + self.path
            self.query_parameters = {}
            self.output_type = OutputType.default
        else:
            raise ValueError('Invalid algorithm URI: ' + algoRef)

    def set_options(self, timeout=300, stdout=False, output=OutputType.default, **query_parameters):
        self.query_parameters = {'timeout':timeout, 'stdout':stdout}
        self.output_type = output
        self.query_parameters.update(query_parameters)
        return self

    # Pipe an input into this algorithm
    def call(self, input1):

        if self.output_type == OutputType.raw:
            return self._postRawOutput(input1)
        elif self.output_type == OutputType.void:
            return self._postVoidOutput(input1)
        else:
            return AlgmResponse.create_algo_response(self.client.postJsonHelper(self.url, input1, **self.query_parameters))

    def _postRawOutput(self, input1):
            # Don't parse response as json
            self.query_parameters['output'] = 'raw'
            response = self.client.postJsonHelper(self.url, input1, parse_response_as_json=False, **self.query_parameters)
            # Check HTTP code and throw error as needed
            if response.status_code == 400:
                # Bad request
                raise ApiError(response.text)
            elif response.status_code == 500:
                raise ApiInternalError(response.text)
            else:
                return response.text

    def _postVoidOutput(self, input1):
            self.query_parameters['output'] = 'void'
            responseJson = self.client.postJsonHelper(self.url, input1, **self.query_parameters)
            if 'error' in responseJson:
                raise ApiError(responseJson['error']['message'])
            else:
                return AsyncResponse(responseJson)
