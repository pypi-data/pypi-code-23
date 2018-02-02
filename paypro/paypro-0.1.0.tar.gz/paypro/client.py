import json, os, requests, ssl 

from paypro.error import ApiConnectionError, InvalidResponseError

class Client:
    API_ENDPOINT = 'https://www.paypro.nl/post_api'
    API_VERSION = 'v1'

    def __init__(self, api_key):
        self.api_key = api_key
        self.params = {}
        self.command = None
        self.ca_cert = self.getCACert()

    def execute(self):
        try:
            response = requests.post(
                self.API_ENDPOINT,
                verify = self.ca_cert,
                data = {
                    'command': self.command,
                    'apikey': self.api_key,
                    'params': json.dumps(self.params)
                }
            )

            return response.json()
        except (requests.exceptions.RequestException, requests.exceptions.Timeout, requests.exceptions.TooManyRedirects) as e:
            raise ApiConnectionError(
                'Could not connect to the PayPro API - {}'.format(str(e))
            )
        except ValueError as e:
            raise InvalidResponseError(
                'The API request returned an invalid response - {}'.format(str(e))
            )

    def setCommand(self, command):
        self.command = command

    def setParam(self, param, value):
        self.params[param] = value

    def setParams(self, params):
        for param, value in params.items():
            self.params[param] = value

    def getCACert(self):
        return os.path.join(os.path.dirname(__file__), 'data/ca-bundle.crt')