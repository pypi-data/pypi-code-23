from typing import Dict, Any, Optional, Union, TextIO, Generator  # noqa
import requests
import json
from datetime import datetime, timedelta
from .errors import LoginError, APIError, TokenError
from .schema import _process_schema


class Client(object):
    """Textile REST API Client"""

    def __init__(self, client_id, client_secret, bundle, api_url="https://api.textile.io"):
        # type: (str, str, str) -> None
        """
        API Client initializer.
        :param client_id: Application/client unique identifier.
        :param client_secret: Application/client secret (see http://docs.textile.io/overview/accounts-security/)
        :param bundle: Application bundle id.
        :param api_url: Base REST API url to use. Default is "https://api.textile.io"
        """
        self.api_url = api_url  # type: str
        self.credentials = None  # type: Optional[Dict[str, Any]]
        self._login(client_id=client_id, client_secret=client_secret, bundle=bundle)

    def _login(self, **login_json):  # type: (Dict[str, Any]) -> None
        r = requests.post("{base}/applications/requestToken".format(base=self.api_url), json=login_json)
        if r.status_code != 200:
            raise LoginError("Unable to obtain access token. Please check credentials.")
        login_json["access_token"] = r.json().get("access_token")
        self.credentials = login_json

    @staticmethod
    def _process_params(params):
        now = datetime.now()
        end = params.pop("end", now).isoformat()
        start = params.pop("start", now - params.pop("lookback", timedelta(days=1))).isoformat()
        types = params.pop("types", None)
        if types is not None:
            if not isinstance(types, list):
                types = [types, ]
            types = ",".join(types)
        return dict(types=types, start="'{}'".format(start), end="'{}'".format(end))

    def get_health(self):  # type: () -> bool
        """
        Check health of REST API endpoint.
        :return: True if main url returns a status code of 200, otherwise False.
        """
        return requests.get(self.api_url).status_code == 200

    def request_features(self, **params):  # type: (Dict[str, Any]) -> Generator[Dict[str, Any]]
        """
        Request all users' features.
        :param start: Start datetime.
        :param end: End datetime.
        :param lookback: Look back time as a timedelta. This value is ignored if `start` is provided.
        :return: Generator of json-parsed dictionaries of features.
        """
        token = self.credentials.get("access_token")
        if token is None:
            raise TokenError("Missing access token. Please login again.")
        headers = dict(Authorization="Bearer {token}".format(token=token))
        info = dict(base=self.api_url, app=self.credentials.get("client_id"))
        with requests.get("{base}/applications/{app}/features".format(**info),
                          headers=headers, params=Client._process_params(params), stream=True) as r:
            if r.status_code != 200:
                raise APIError("Unable to access API. Please check credentials.")
            for chunk in _process_chunks(r.iter_lines(chunk_size=None)):
                yield chunk

    def download_features(self, path_or_buf, **params):  # type: (Union[str, TextIO], Dict[str, Any]) -> None
        """
        Download all users' features to a file.
        :param path_or_buf: Path to file or a buffer/file-like object to write to.
        :param start: Start datetime.
        :param end: End datetime.
        :param lookback: Look back time as a timedelta. This value is ignored if `start` is provided.
        """
        token = self.credentials.get("access_token")
        if token is None:
            raise TokenError("Missing access token. Please login again.")
        headers = dict(Authorization="Bearer {token}".format(token=token))
        info = dict(base=self.api_url, app=self.credentials.get("client_id"))
        with requests.get("{base}/applications/{app}/features".format(**info),
                          headers=headers, params=Client._process_params(params), stream=True) as r:
            if r.status_code != 200:
                raise APIError("Unable to access API. Please check credentials.")
            chunks = r.iter_lines(chunk_size=None)
            if isinstance(path_or_buf, str):
                with open(path_or_buf, "w+") as f:
                    f.writelines(json.dumps(chunk) + "\n" for chunk in _process_chunks(chunks))
            else:
                path_or_buf.writelines(json.dumps(chunk) + "\n" for chunk in _process_chunks(chunks))


def _process_chunks(chunks):
    for chunk in chunks:
        if chunk:
            try:
                line = json.loads(chunk.decode("utf-8"))
                output = {"timestamp": line["ts"]}
                output.update(_process_schema(line))
                yield output
            except (TypeError, KeyError):
                pass
