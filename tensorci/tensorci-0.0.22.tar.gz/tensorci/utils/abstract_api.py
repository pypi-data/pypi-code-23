import requests
from tensorci import log
from tensorci.definitions import tci_keep_alive


class AbstractApi(object):
  """
  Provides a RESTful interface to the API url of choice.
  Wrapper around the 'requests' library.

  Allows for specification of:
    - Base url of API
    - Route to hit
    - Method to use (GET, POST, PUT, and DELETE supported)
    - Payload (auto-converted into query params for GET & DELETE requests)
    - Form data
    - If streaming request should be made
    - Base headers (used on all requests)
    - Request-specific headers (can overwrite base headers)
    - Auth headers (can either be static or read a token from a provided function)

  Basic usage:
    api_client = AbstractApi(base_url='https://myurl.com/api',
                             base_headers={'My-Header': 'Always include this header'},
                             auth_header_name='My-Special-Token',
                             auth_header_val='super-secret-token')

    resp = api_client.get('/my-route', payload={'key': 'val'})

    resp.status         # 200
    resp.json           # => {'key': 'parsed json response'}
    resp.headers        # {'My-Response-Header': 'some value'}
    resp.response_obj   # 'requests.models.Response' class instance
  """

  def __init__(self, base_url=None, base_headers=None, auth_header_name=None,
               auth_header_val=None, auth_header_val_getter=None):
    """
    :param str base_url: Base url of the API you wish to hit
    :param dict base_headers: Headers to send with every request
    :param str auth_header_name: Name of authorization header
    :param str auth_header_val: Value of authorization header (overwritten by auth_header_val_getter)
    :param function auth_header_val_getter: Function that returns the value of the authorization header
    """
    self.base_url = base_url
    self.base_headers = base_headers or {}
    self.auth_header_name = auth_header_name
    self.auth_header_val = auth_header_val
    self.auth_header_val_getter = auth_header_val_getter

  def get(self, route, **kwargs):
    """
    Make a GET request to the given route

    :param str route: Route to hit on top of 'self.base_url'
    ** See 'self.make_request' for accepted kwargs params **

    :return: an API response object
    :rtype: AbstractApiResponse
    """
    return self.make_request('get', route, **kwargs)

  def post(self, route, **kwargs):
    """
    Make a POST request to the given route

    :param str route: Route to hit on top of 'self.base_url'
    ** See 'self.make_request' for accepted kwargs params **

    :return: an API response object
    :rtype: AbstractApiResponse
    """
    return self.make_request('post', route, **kwargs)

  def put(self, route, **kwargs):
    """
    Make a PUT request to the given route

    :param str route: Route to hit on top of 'self.base_url'
    ** See 'self.make_request' for accepted kwargs params **

    :return: an API response object
    :rtype: AbstractApiResponse
    """
    return self.make_request('put', route, **kwargs)

  def delete(self, route, **kwargs):
    """
    Make a DELETE request to the given route

    :param str route: Route to hit on top of 'self.base_url'
    ** See 'self.make_request' for accepted kwargs params **

    :return: an API response object
    :rtype: AbstractApiResponse
    """
    return self.make_request('delete', route, **kwargs)

  def make_request(self, method, route, payload=None, headers=None, stream=False,
                   mp_upload_monitor=None, log_on_error=True, exit_on_error=True):
    """
    Actually perform the API call.

    :param str method:
      API method to perform. Valid options: 'get', 'post', 'put', 'delete'.
    :param str route:
      API route to hit on top of self.base_url
    :param dict payload:
      Payload to provide with request. For GET and DELETE requests, these are converted into query params.
    :param dict headers:
      Request-specific headers. Will overwrite any self.base_headers with the same key.
    :param bool stream:
      Whether to make a streaming request
    :param mp_upload_monitor:
      Multipart encoder monitor for form-uploaded data
      :type: requests_toolbelt.multipart.encoder.MultipartEncoderMonitor
    :param bool log_on_error:
      Whether to log an error message if the request fails
    :param bool exit_on_error:
      Whether to exit if the request fails
    :return: an API response object
    :rtype: AbstractApiResponse
    """
    # Get the proper method to call on the 'requests' object (get, post, put, or delete).
    request = getattr(requests, method)

    # Build up kwargs to pass to the requests method call.
    request_kwargs = {
      'headers': self.build_request_headers(headers=headers),
      'stream': stream
    }

    if method in ('get', 'delete'):
      # Set the payload as query params for GET and DELETE requests
      request_kwargs['params'] = payload or {}
    elif mp_upload_monitor:
      # If multipart encoder monitor is provided, assign that to the data kwarg
      request_kwargs['data'] = mp_upload_monitor
    else:
      # Otherwise, just set the payload as json
      request_kwargs['json'] = payload or {}

    try:
      # Make the request
      response = request(self.base_url + route, **request_kwargs)
    except KeyboardInterrupt:
      # Allow the user to kill it if taking too long
      exit(0)
    except BaseException as e:
      log('Unknown Error while making request: {}'.format(e))
      exit(1)

    # Create an abstract api response
    api_resp = AbstractApiResponse(response,
                                   stream=stream,
                                   mp_upload=bool(mp_upload_monitor),
                                   log_on_error=log_on_error,
                                   exit_on_error=exit_on_error)

    return api_resp

  def build_request_headers(self, headers={}):
    """
    Build up headers for a request.

    Order in which headers are constructed:
      (1) Start as self.base_headers
      (2) Add key-val pairs from headers param
      (3) Add auth header

      **Note** Header keys can be overwritten if ^this order isn't noted

    :param dict headers: Request-specific headers
    :return: All headers for this request
    :rtype: dict
    """
    # Start with base headers
    all_headers = self.base_headers

    if headers:
      # Add request-specific headers if they exist
      for k, v in headers.items():
        all_headers[k] = headers[k]

    # Return early if no authorization header
    if not self.auth_header_name:
      return all_headers

    # auth_header_val_getter takes precedent over auth_header_val
    if self.auth_header_val_getter:
      all_headers[self.auth_header_name] = self.auth_header_val_getter()
    elif self.auth_header_val:
      all_headers[self.auth_header_name] = self.auth_header_val

    return all_headers


class AbstractApiResponse(object):
  """
  Interface to an API response from AbstractApi.

  Will attempt to parse a JSON response upon initialization, and will
  raise an ApiException if the status code doesn't equal 200 or 201.
  """

  def __init__(self, response_obj, stream=False, mp_upload=False,
               log_on_error=True, exit_on_error=True):
    """
    :param response_obj:
      API response object returned by the 'requests' library
      :type: requests.Response
    :param bool stream:
      Whether request was a streaming request
    :param bool mp_upload:
      Whether request was a multi-part upload
    :param bool log_on_error:
      Whether to log an error message if the request failed
    :param bool exit_on_error:
      Whether to exit if the request failed
    """
    self.response_obj = response_obj
    self.stream = stream
    self.mp_upload = mp_upload
    self.log_on_error = log_on_error
    self.exit_on_error = exit_on_error

    self.headers = response_obj.headers
    self.status = response_obj.status_code
    self.ok = self.status in (200, 201)

    # Don't parse json for successful streaming requests and multi-part uploads.
    if (self.stream or self.mp_upload) and self.ok:
      self.json = None
    else:
      self.json = self.parse_json_resp()

    if not self.ok:
      if self.log_on_error:
        self.log_error()

      if self.exit_on_error:
        exit(1)

  def parse_json_resp(self):
    """
    Attempt to parse a JSON response, defaulting to an empty dict.

    :return: Parsed JSON response
    :rtype: dict or list (dict if error)
    """
    try:
      return self.response_obj.json() or {}
    except:
      return {}

  def log_error(self):
    """
    Log the error parsed from the JSON body.

    If a 'log' key was found in the body, it's assumed that this is
    the specified error message that should be shown to the user.

    Otherwise, an error message is constructed from the 'error' key,
    the response's status code, and custom error 'code' key.
    """
    if self.ok:
      return

    # Log the provided 'log' message if it exists.
    provided_err_log_msg = self.json.get('log')

    if provided_err_log_msg:
      log(provided_err_log_msg)
      return

    # If log message not provided, construct an error message.
    err_msg = 'Request failed'
    error = self.json.get('error')
    code = self.json.get('code')

    if error:
      err_msg += ' with error: {}'.format(error)

    if code:
      err_msg += '; code={}'.format(code)

    err_msg += '; status={}'.format(self.status)

    log(err_msg)

  def log_stream(self, chunk_size=10, lines_to_ignore=(tci_keep_alive)):
    """
    Log the streaming response by parsing and iterating over lines of the response.

    :param int chunk_size: Chunk size to parse response with (default=10)
    :param tuple(str) lines_to_ignore: Tuple of log messages to ignore.
    """
    if not self.stream:
      return

    try:
      for line in self.response_obj.iter_lines(chunk_size=chunk_size):
        if not line or line in lines_to_ignore:
          continue

        log(line)
    except KeyboardInterrupt:
      exit(0)
    except BaseException as e:
      log('Error while parsing logs: {}'.format(e))
