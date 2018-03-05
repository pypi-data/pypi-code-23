from time import time

import requests
import re


class APIClient:

    DEFAULT_VERSION = "v1_1"

    def __init__(self, id_gate, gate_secret_key, version=DEFAULT_VERSION):
        """
        Create an instance of API Client. If you want you can specify the API version

        :type id_gate: str
        :param id_gate: Your gate id

        :type gate_secret_key: str
        :param gate_secret_key: Your gate secret key

        :type version: str
        :param version: API version
        """
        # APIClient.verify_api_version(version)
        self._id_gate = id_gate
        self._gate_secret_key = gate_secret_key
        self._version = version
        self._api_token = None
        self._api_endpoint = "https://api.logup.co/" + self._version
        self._token_expiration_date = 0

    @staticmethod
    def can_proceed(response):
        # type: (requests.Response) -> bool
        """
        Check the response code received and verify if you can proceed or not.

        :type response: requests.Response
        :param response: Response received from the server

        :rtype: bool
        :return:
        """
        return not (response.status_code >= 400 or response.status_code < 200)

    def construct_headers(self):
        # type: () -> dict
        """
        Create and return authorization headers

        :rtype: dict
        :return: Authorization headers
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer " + self._api_token
        }
        if self._version == "dev":
            headers["__devHeader"] = "ACbidw8CnSijtjtVQtbG2L6gAusbLQoQaZZfR5PS5GdGLWjM9DERbtGHJMPAjeMYLqxSy93P2gGvt9eQPF6M732sqECoxgMjTzTKijEfGYa75ixtJ44J6SAi4hjwWA6u"
        return headers

    def delete(self, path, fields):
        # type: (str) -> requests.Response
        """
        Do delete request

        :type path: str
        :param path: Endpoint path to be called

        :type fields: dict
        :param fields: Endpoint path to be called

        :rtype: requests.Response
        :return: Response received from the server
        """
        self.get_auth_token()
        endpoint_url = self._api_endpoint + path
        return requests.delete(endpoint_url, headers=self.construct_headers(), json=fields)

    def get(self, path):
        # type: (str) -> requests.Response
        """
        Do get request

        :type path: str
        :param path: Endpoint path to be called

        :rtype: requests.Response
        :return: Response received
        """
        self.get_auth_token()
        endpoint_url = self._api_endpoint + "/" + path
        return requests.get(endpoint_url, headers=self.construct_headers())

    def get_auth_token(self):
        """
        Get authentication token an store it into the _api_token parameter.
        """
        if self._api_token is None:
            endpoint_url = self._api_endpoint + "/oauth/token"
            headers = {"Content-Type": "application/json", "Accept": "application/json", "Charset": "UTF-8",
                       "__devHeader": "ACbidw8CnSijtjtVQtbG2L6gAusbLQoQaZZfR5PS5GdGLWjM9DERbtGHJMPAjeMYLqxSy93P2gGvt9eQPF6M732sqECoxgMjTzTKijEfGYa75ixtJ44J6SAi4hjwWA6u"}

            data = {"client_id": self._id_gate, "client_secret": self._gate_secret_key,
                    "grant_type": "client_credentials"}
            response = requests.post(endpoint_url, headers=headers, json=data)
            if response.status_code == 201:
                self._api_token = response.json()["access_token"]
                self._token_expiration_date = int(time()) + response.json()["expires_in"]
            else:
                print(response.json())
                if 'errorMessage' not in response.json():
                    error = response.json()["message"]
                else:
                    error = response.json()["errorMessage"]
                raise RuntimeError("Failed : HTTP error code : " + str(response.status_code) + " and error " + error)

    @property
    def is_token_expired(self):
        # type: () -> bool
        """
        Check if the current token has expired or not

        :rtype: bool
        :return True if the token has expired, otherwise
        """
        return self._token_expiration_date - 10 <= time()

    def post(self, path, fields):
        # type: (str, dict) -> requests.Response
        """
        Do post request

        :type path: str
        :param path: Endpoint path to be called

        :type fields: dict
        :param fields: Fields to be sent to logup server.

        :rtype: requests.Response
        :return: Response received from the server
        """
        self.get_auth_token()
        endpoint_url = self._api_endpoint + "/" + path
        return requests.post(endpoint_url, headers=self.construct_headers(), json=fields)

    def put(self, path, fields):
        # type: (str, dict) -> requests.Response
        """
        Do put request

        :type path: str
        :param path: Endpoint path to be called

        :type fields: dict
        :param fields: Fields to be sent to logup server.

        :rtype: requests.Response
        :return Response received from the server
        """
        self.get_auth_token()
        endpoint_url = self._api_endpoint + "/" + path
        return requests.put(endpoint_url, headers=self.construct_headers(), json=fields)

    @staticmethod
    def verify_api_version(version):
        """
        Validate the API version param received.

        :type version: str
        :param version: Version to be validated
        """
        if not APIClient.DEFAULT_VERSION == version:
            if re.match("^v(\\d{1,2}_\\d{1,3})$", version) is None:
                raise ValueError("Invalid version entered! Check the version value, it should be something like v#_#")
