import requests
import json
import sys
import time


class ServiceLayerClient:

    reflector_url = None
    path = None
    sentinel_url = None
    request_headers = None
    reflector_token = None

    def __init__(self, reflector_url, path, sentinel_url, request_headers):
        self.reflector_url = reflector_url
        self.path = path
        self.sentinel_url = sentinel_url
        self.request_headers = request_headers
        self._set_reflector_token()

    def _set_reflector_token(self):
        """
        Gets ands sets reflector token from sentinel for a specific path
        """
        sentinel_url_with_path = "{}&path={}".format(self.sentinel_url, self.path)
        try:
            response_data = requests.get(url=sentinel_url_with_path)
            data = json.loads(response_data.content)
            self.reflector_token = data['result'][0]['token']
        except Exception:
            raise IOError("Could not get a Reflector token")

    def _get_request_with_token(self, request_params):
        """
        Returns a full request url with a reflector token

        :param request_params:string: parameters of the request
        :return: full request url
        """
        if request_params:
            return '{}?path={}&{}&token={}'.format(self.reflector_url, self.path, request_params, self.reflector_token)
        return '{}?path={}&token={}'.format(self.reflector_url, self.path, self.reflector_token)

    def fetch_data(self, request_parameters=None, attempt=0):
        """
        Fetches data from the ServiceLayer using the set parameters.

        :param request_parameters:string: parameters of the request
        :param attempt: int: the amount of attempts that are already done for this request
        :return: array/list: array of dictionaries constructed from the json retrieved by executing a ServiceLayer request
        """

        response_data = None
        total_exceptions = 0
        no_data_retrieved_msg = "No data retrieved from service layer"

        request_with_token = self._get_request_with_token(request_parameters)
        print("execute url (attempt {}): {} ".format(attempt + 1, request_with_token))

        try:
            # Wait for a bit if this is not the first request
            time.sleep(0.5 * attempt)
            response_data = requests.get(url=request_with_token, headers=self.request_headers)

        except Exception as e:
            total_exceptions += 1
            exception = e.message if hasattr(e, 'message') else e
            print("-- exception occurred while fetching data: {0} --".format(exception))

        if response_data.status_code == 503:
            # stop execution as soon as  the maximum amount of tries is exceeded
            if attempt >= 3:
                raise IOError("{}: Service unavailable".format(no_data_retrieved_msg))

            # Try the function once more
            return self.fetch_data(request_parameters, attempt + 1)

        elif response_data.status_code == 401:
            # stop execution: access denied
            if attempt >= 3:
                raise IOError("{}: Access denied".format(no_data_retrieved_msg))

            # Get a new token and try the function once more
            self._set_reflector_token()
            return self.fetch_data(request_parameters, attempt + 1)

        elif response_data.status_code != 200:
            # stop execution: incorrect request, service unavailable
            raise IOError("{}: Incorrect request".format(no_data_retrieved_msg))

        return _parse_data(response_data.text)

    def test_query_connection(self, request_parameters=None):
        """
        Function to test request to ServiceLayer using the set headers

        :return: int: number denoting the total results related to the query executed on ServiceLayer or an exception.
        """

        self._set_reflector_token()
        try:
            response_data = requests.get(url=self._get_request_with_token(request_parameters),
                                         headers=self.request_headers)
            return int(response_data.headers['X-StudyPortals-Total'])

        except Exception as e:
            print("Error occurred while testing the connection to ServiceLayer: {}".format(e))
            sys.exit(1)


def _parse_data(response):
    """
    Function which parses json into an array of dictionaries. It is used to parse the json response from the
    ServiceLayer to dictionaries enabling the retrieval of data in a convenient way using the properties of a
    dictionary.

    If the response is not a dictionary - return it.

    :param response: string json content
    :return: array/list: Array of dictionaries constructed from json or the response in json
    """
    try:
        json_response = json.loads(response)
    except ValueError:
        return None

    if isinstance(json_response, dict):
        return [value for key, value in json_response.items()]
    return json_response
