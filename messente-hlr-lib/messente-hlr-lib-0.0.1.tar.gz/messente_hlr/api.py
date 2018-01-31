"""
   Copyright 2018 Messente Communications Ltd.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from functools import wraps

from messente_hlr import client

URL = "https://api.messente.com/hlr/"


def _validate_input(func):
    # decorator for validating that passed arguments are not None
    @wraps(func)
    def wrapper(*args):
        for arg in args[1:]:
            if arg is None:
                raise ValueError("{} should be string".format(arg))
        return func(*args)

    return wrapper


class Api(object):
    """Main class for hlr api"""

    def __init__(self, username, password, endpoint=URL):
        """Initialize hlr api

        Args:
            username (str): api username. Can be obtained from dashboard

            password (str): api password. Can be obtained from dashboard

            endpoint (str): api endpoint. Can be obtained from dashboard
        """
        self.rest_client = client.RestClient(endpoint, username, password)

    @_validate_input
    def sync(self, numbers):
        """Async call.

        Args:
            numbers (list): List of numbers to call ["+123123123", ...].

        Returns:
            List of hlr data for given numbers
        """
        json = {
            'numbers': numbers
        }

        response = self.rest_client.post("sync", json=json)
        return response['result']

    @_validate_input
    def async(self, numbers, callback):
        """Async call.

        Args:
            numbers (list): List of numbers to call ["+123123123", ...].
            callback (str): Callback url where you want your response

        Returns:
            Request id
        """
        json = {
            'numbers': numbers,
            'callback': callback
        }

        response = self.rest_client.post("async", json=json)
        return response['request_id']
