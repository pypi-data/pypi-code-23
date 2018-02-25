import json
import urllib.parse


class HttpRequest(object):
    """Class representing a http request"""

    def __init__(self, url, method='GET', data=None, query_params=None,
                 headers=None):
        """Initializes a generic HTTP request

        Args:
            url (str):
                The url of the request. Supported schemes: http and https
            method (str):
                The HTTP verb
            query_params (dict):
                Mapping of query parameters
            data:
                The payload of the request if the method allows.
            headers (dict):
                Headers for the request
        """
        self.url = self.validate_url(url)
        self.method = self.validate_method(method)
        self.query_params = self.validate_query_params(query_params or {})
        self.data = self.validate_data(data)

        self.headers = self.get_default_headers()
        self.headers.update(self.validate_headers(headers) or {})

    def validate_url(self, url):
        """Validates that the url is provided and has the proper scheme"""
        if not url:
            raise ValueError('url is required')
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            raise ValueError('Invalid schema: {}'.format(parsed.scheme))
        return url

    def validate_method(self, method):
        """Validates the http verb"""
        if method not in ('GET', 'POST', 'OPTIONS', 'PATCH', 'PUT'):
            raise ValueError('Invalid http method: {}'.format(method))
        return method

    def validate_headers(self, headers):
        """Validates the http headers"""
        if headers and not isinstance(headers, dict):
            raise TypeError('Invalid headers type. It should be a dict')
        return headers

    def validate_data(self, data):
        """Validates the payload"""
        return data

    def validate_query_params(self, query_params):
        """Validates the query parameters"""
        if query_params and not isinstance(query_params, dict):
            raise TypeError('Invalid type for query dict')
        return query_params

    def get_default_headers(self):
        return {}

    @property
    def content_type(self):
        return self.headers.get('Content-Type', 'application/octet-stream')


class GetRequest(HttpRequest):
    """A HTTP GET request"""

    def __init__(self, url, query_params=None, headers=None):
        super(GetRequest, self).__init__(url=url, method='GET',
                                         query_params=query_params,
                                         headers=headers, data=None)


class PostRequest(HttpRequest):
    """A HTTP POST request"""

    def __init__(self, url, data=None, query_params=None, headers=None):
        super(PostRequest, self).__init__(url=url, data=data,
                                          query_params=query_params,
                                          headers=headers, method='POST')


class XhrRequest(HttpRequest):
    """A XHR Post request"""

    def get_default_headers(self):
        return {'X-Requested-With': 'XMLHttpRequest'}


class JsonRequest(HttpRequest):
    """A generic JSON request.

    The data must be an object that can be safely encoded as JSON.

    Examples:

        JsonRequest('http://example.com', 'POST', data={'hello': 'world'})
    """

    def get_default_headers(self):
        """Returns the json request specific headers"""
        return {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
            'Accept': 'application/json, application/*;q=0.9, */*;q=0.8'
        }

    def validate_data(self, data):
        """Validates the data by converting it to json"""
        if data:
            try:
                return json.dumps(data, separators=(',', ':'))
            except ValueError:
                raise ValueError(
                    'Unable to encode as JSON the request data: {}'.format(
                        data))
        else:
            return data
