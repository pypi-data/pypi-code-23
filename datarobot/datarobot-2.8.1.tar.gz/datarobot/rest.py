"""This module is not considered part of the public interface. As of 2.3, anything here
may change or be removed without warning."""

import platform
import os

import requests
import six
import trafaret as t
from requests_toolbelt.multipart.encoder import MultipartEncoder
from six.moves.urllib_parse import urlparse

from .enums import DEFAULT_TIMEOUT
from . import __version__
from .utils import to_api
from . import errors


class RESTClientObject(requests.Session):
    """
    Parameters
        connect_timeout
            timeout for http request and connection
        headers
            headers for outgoing requests
    """
    @classmethod
    def from_config(cls, config):
        return cls(auth=config.token, endpoint=config.endpoint,
                   connect_timeout=config.connect_timeout, verify=config.ssl_verify,
                   user_agent_suffix=config.user_agent_suffix)

    def __init__(self, auth=None, endpoint=None, connect_timeout=DEFAULT_TIMEOUT.CONNECT,
                 verify=True, user_agent_suffix=None):
        super(RESTClientObject, self).__init__()
        # Note: As of 2.3, `endpoint` is required
        self.endpoint = endpoint
        self.domain = '{}://{}'.format(urlparse(self.endpoint).scheme,
                                       urlparse(self.endpoint).netloc)
        self.token = auth
        if connect_timeout is None:
            connect_timeout = DEFAULT_TIMEOUT.CONNECT
        self.connect_timeout = connect_timeout
        self.user_agent_header = self._make_user_agent_header(suffix=user_agent_suffix)
        self.headers.update(self.user_agent_header)
        self.token_header = {'Authorization': 'Token {}'.format(self.token)}
        self.headers.update(self.token_header)
        self.verify = verify

    @staticmethod
    def _make_user_agent_header(suffix=None):
        agent_components = []
        agent_components.append('DataRobotPythonClient/{}'.format(__version__))
        agent_components.append('({} {} {})'.format(platform.system(),
                                                    platform.release(),
                                                    platform.machine()))
        if suffix:
            agent_components.append(suffix)
        return {'User-Agent': ' '.join(agent_components)}

    def _join_endpoint(self, url):
        return '{}/{}'.format(self.endpoint, url)

    def strip_endpoint(self, url):
        trailing = '' if self.endpoint.endswith('/') else '/'
        expected = '{}{}'.format(self.endpoint, trailing)
        if not url.startswith(expected):
            raise ValueError('unexpected url format: {} does not start with {}'.format(url,
                                                                                       expected))
        return url.split(expected)[1]

    def request(self, method, url, join_endpoint=False, **kwargs):
        kwargs.setdefault('timeout', (self.connect_timeout, DEFAULT_TIMEOUT.READ))
        if not url.startswith('http') or join_endpoint:
            url = self._join_endpoint(url)
        response = super(RESTClientObject, self).request(method, url, **kwargs)
        if not response:
            handle_http_error(response)
        return response

    def get(self, url, params=None, **kwargs):
        return self.request('get', url, params=to_api(params), **kwargs)

    def post(self, url, data=None, **kwargs):
        if data:
            kwargs['json'] = to_api(data)
        return self.request('post', url, **kwargs)

    def patch(self, url, data=None, **kwargs):
        if data:
            kwargs['json'] = to_api(data)
        return self.request('patch', url, **kwargs)

    def build_request_with_file(self, method, url,
                                fname,
                                form_data=None,
                                content=None,
                                file_path=None,
                                filelike=None,
                                read_timeout=DEFAULT_TIMEOUT.READ,
                                file_field_name='file'):
        """Build request with a file that will use special
        MultipartEncoder instance (lazy load file).


        This method supports uploading a file on local disk, string content,
        or a file-like descriptor. ``fname`` is a required parameter, and
        only one of the other three parameters can be provided.

        Parameters
        ----------
        method : str.
            Method of request. This parameter is required, it can be
            'POST' or 'PUT' either 'PATCH'.
        url : str.
            Url that will be used it this request.
        fname : name of file
            This parameter is required, even when providing a file-like object
            or string content.
        content : str
            The content buffer of the file you would like to upload.
        file_path : str
            The path to a file on a local file system.
        filelike : file-like
            An open file descriptor to a file.
        read_timeout : float
            The number of seconds to wait after the server receives the file that we are
            willing to wait for the beginning of a response. Large file uploads may take
            significant time.
        file_field_name : str
            The name of the form field we will put the data into (Defaults to 'file').

        Returns
        -------
        response : response object.

        """

        bad_args_msg = ('Upload should be used either with content buffer '
                        'or with path to file on local filesystem or with '
                        'open file descriptor')
        assert sum((bool(content),
                    bool(file_path),
                    bool(filelike))) == 1, bad_args_msg

        if file_path:
            if not os.path.exists(file_path):
                raise ValueError(
                    u'Provided file does not exist {}'.format(file_path))
            fields = {file_field_name: (fname, open(file_path, 'rb'))}

        elif filelike:
            filelike.seek(0)
            fields = {file_field_name: (fname, filelike)}
        else:
            if not isinstance(content, six.binary_type):
                raise AssertionError('bytes type required in content')
            fields = {file_field_name: (fname, content)}

        form_data = form_data or {}
        data_for_encoder = to_api(form_data)
        data_for_encoder.update(fields)

        encoder = MultipartEncoder(fields=data_for_encoder)
        headers = {'Content-Type': encoder.content_type}
        return self.request(method, url, headers=headers, data=encoder,
                            timeout=(self.connect_timeout, read_timeout))


def _http_message(response):
    if response.status_code == 401:
        message = ('The server is saying you are not properly '
                   'authenticated. Please make sure your API '
                   'token is valid.')
    elif response.headers['content-type'] == 'application/json':
        message = response.json()
    else:
        message = response.content.decode('ascii')[:79]
    return message


def handle_http_error(response):
    message = _http_message(response)
    if 400 <= response.status_code < 500:
        exception_type = errors.ClientError
        # One-off approach to raising special exception for now. We'll do something more
        # systematic when we have more of these:
        try:
            parsed_json = response.json()  # May raise ValueError if response isn't JSON
            if parsed_json.get('errorName') == 'JobAlreadyAdded':
                exception_type = errors.JobAlreadyRequested
        except ValueError:
            pass
        template = '{} client error: {}'
        exc_message = template.format(response.status_code, message)
        raise exception_type(exc_message, response.status_code)
    else:
        template = '{} server error: {}'
        exc_message = template.format(response.status_code, message)
        raise errors.ServerError(exc_message, response.status_code)


class DataRobotClientConfig(object):
    """
    This class contains all of the client configuration variables that are known to
    the DataRobot client.

    Values are allowed to be None in this object. The __init__ of RESTClientObject will
    provide any defaults that should be applied if the user does not specify in the config
    """
    _converter = t.Dict({
        t.Key('endpoint'): t.String(),
        t.Key('token'): t.String(),
        t.Key('connect_timeout', optional=True): t.Int(),
        t.Key('ssl_verify', optional=True): t.Or(t.Bool(), t.String()),
        t.Key('user_agent_suffix', optional=True): t.String(),
    }).allow_extra('*')
    _fields = {k.to_name or k.name for k in _converter.keys}

    def __init__(self, endpoint, token, connect_timeout=None, ssl_verify=True,
                 user_agent_suffix=None):
        self.endpoint = endpoint
        self.token = token
        self.connect_timeout = connect_timeout
        self.ssl_verify = ssl_verify
        self.user_agent_suffix = user_agent_suffix

    @classmethod
    def from_data(cls, data):
        checked = {k: v
                   for k, v in cls._converter.check(data).items()
                   if k in cls._fields}
        return cls(**checked)
