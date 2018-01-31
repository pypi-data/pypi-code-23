import requests
import binascii
import uuid
import hashlib
import json
import functools
from datetime import datetime

from adobe_analytics.suite import Suite


class Client(object):
    DEFAULT_ENDPOINT = "https://api.omniture.com/admin/1.4/rest/"

    def __init__(self, username, password, endpoint=DEFAULT_ENDPOINT):
        self.username = username
        self.password = password
        self.endpoint = endpoint

    @classmethod
    def from_json(cls, file_path):
        with open(file_path, mode="r") as json_file:
            credentials = json.load(json_file)
        return cls(credentials["username"], credentials["password"])

    @functools.lru_cache(maxsize=None)
    def suites(self):
        response = self.request("Company", "GetReportSuites")
        suites = [self._suite_from_dict(suite, self) for suite in response["report_suites"]]
        return {suite.id: suite for suite in suites}

    @staticmethod
    def _suite_from_dict(suite_dict, client):
        return Suite(name=suite_dict["site_title"], suite_id=suite_dict["rsid"], client=client)

    def request(self, api, method, data=None):
        """ Compare with https://marketing.adobe.com/developer/api-explorer """
        api_method = '{0}.{1}'.format(api, method)
        data = data or dict()

        response = requests.post(
            self.endpoint,
            params={'method': api_method},
            data=json.dumps(data),
            headers=self._build_headers()
        )
        json_response = response.json()
        if isinstance(json_response, dict) and ("error" in json_response):
            self.raise_error(json_response)
        return json_response

    def _build_headers(self):
        nonce = str(uuid.uuid4())
        base64nonce = binascii.b2a_base64(binascii.a2b_qp(nonce))
        created_date = datetime.utcnow().isoformat() + 'Z'
        sha = nonce + created_date + self.password
        sha_object = hashlib.sha1(sha.encode())
        password_64 = binascii.b2a_base64(sha_object.digest())
        
        properties = {
            "Username": self.username,
            "PasswordDigest": password_64.decode().strip(),
            "Nonce": base64nonce.decode().strip(),
            "Created": created_date
        }
        header = 'UsernameToken ' + self._serialize_header(properties)
        return {'X-WSSE': header}

    @staticmethod
    def _serialize_header(properties):
        header = ['{key}="{value}"'.format(key=k, value=v) for k, v in properties.items()]
        return ', '.join(header)

    @staticmethod
    def raise_error(response):
        error_description = response["error_description"]

        if response["error"] == "report_not_ready":
            raise FileNotFoundError(error_description)
        else:
            raise Exception(error_description)

    def __repr__(self):
        return "User: {0} | Endpoint: {1}".format(self.username, self.endpoint)
