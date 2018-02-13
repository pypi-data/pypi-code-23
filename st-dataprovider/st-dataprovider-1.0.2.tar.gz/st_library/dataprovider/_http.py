# Copyright 2017 Shortest Track Company. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing permissions and limitations under
# the License.

"""Implements HTTP client helper functionality."""
from __future__ import absolute_import
from __future__ import unicode_literals
from future import standard_library
standard_library.install_aliases()  # noqa
from builtins import str
from past.builtins import basestring
from builtins import object

import datetime
import json
import urllib.request
import urllib.parse
import urllib.error
import httplib2
import logging
import sys
import st_library.dataprovider as datapv


log = logging.getLogger(__name__)


# TODO(nikhilko): Start using the requests library instead.


class RequestException(Exception):

  def __init__(self, status, content):
    self.status = status
    self.content = content
    self.message = 'HTTP request failed'
    # Try extract a message from the body; swallow possible resulting ValueErrors and KeyErrors.
    try:
      error = json.loads(content)['error']
      if 'errors' in error:
        error = error['errors'][0]
      self.message += ': ' + error['message']
    except Exception:
      lines = content.split('\n') if isinstance(content, basestring) else []
      if lines:
        self.message += ': ' + lines[0]

  def __str__(self):
    return self.message


class Http(object):
  """A helper class for making HTTP requests.
  """

  # Reuse one Http object across requests to take advantage of Keep-Alive, e.g.
  # for BigQuery queries that requires at least ~5 sequential http requests.
  #
  # TODO(nikhilko):
  # SSL cert validation seemingly fails, and workarounds are not amenable
  # to implementing in library code. So configure the Http object to skip
  # doing so, in the interim.
  http = httplib2.Http(timeout = 50000)
  http.disable_ssl_certificate_validation = True

  def __init__(self):
    pass

  @staticmethod
  def request(url, args=None, data=None, headers=None, method=None,
              credentials=None, raw_response=False, stats=None):
    """Issues HTTP requests.

    Args:
      url: the URL to request.
      args: optional query string arguments.
      data: optional data to be sent within the request.
      headers: optional headers to include in the request.
      method: optional HTTP method to use. If unspecified this is inferred
          (GET or POST) based on the existence of request data.
      credentials: optional set of credentials to authorize the request.
      raw_response: whether the raw response content should be returned as-is.
      stats: an optional dictionary that, if provided, will be populated with some
          useful info about the request, like 'duration' in seconds and 'data_size' in
          bytes. These may be useful optimizing the access to rate-limited APIs.
    Returns:
      The parsed response object.
    Raises:
      Exception when the HTTP request fails or the response cannot be processed.
    """
    if headers is None:
      headers = {}

    headers['user-agent'] = 'GoogleCloudDataLab/1.0'
#     headers['Authorization'] = "Token "+os.environ['SHORTESTTRACK_API_TOKEN']
#     headers['Authorization'] = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4MTIyYTNkMy1lZmQ2LTQwMjYtOGVlZi04MzMzNmJlNmFkNzciLCJpc3MiOiJzaG9ydGVzdHRyYWNrLXVhYSIsImF1dGhvcml0aWVzIjpbIlJPTEVfQ09NUEFOWV9BRE1JTiJdLCJkamFuZ29Vc2VySWQiOiI5OTkiLCJjbGllbnRfaWQiOiJ3ZWJfYXBwIiwiYXVkIjoid2ViX2FwcCIsImNvbXBhbnlJZCI6InRlc3Rfc2hvcnRlc3R0cmFja19mdW5jdGlvbmFsaXR5IiwiZGphbmdvVG9rZW4iOiI5NjUxYmQzZGJiZWExZDQ5YjM1MzhjZjRjMDU1MWMzODhiOGVlNzZlIiwic2NvcGUiOlsib3BlbmlkIl0sImV4cCI6MTUxNTc3OTc1MSwiaWF0IjoxNTE1NDc5NzUxLCJqdGkiOiJjNmIzNjFjYy1jNWE5LTRjMDMtOGQxOC1kM2QxMzA0ODVlYzMiLCJlbWFpbCI6InB1YmxpYy1hZG1pbkBsb2NhbGhvc3QifQ.KTRtKFleC0NHPxqldlXhb6SxIGHSh2WEAboyLg5NZOteZ-4IceCWA06yjVuO8XX85Q3Z5rSrTrBM7RG2Tj0EewfrJknnNLAQ5-Yw23dO7TgZLkvNufbykGjr4VdxvofIsr4jw4xghV3z3HT-buxKMxg32PFx24N1ciNZ8l66wSLVHNwVYFXsjhNzbUV7YshmVibPQnqjavI9JL9Zie44AKUauwkGNpuC9a-H4iOp_iHQxG9EgW4-v932T_gurPfLEfVsvK2K-cL7q9KBpzB84tFUeBgkCrLCMvhjaYwMJ695FDu8sQ6jcSWzCIH8PMWHSG__OhurgJKpuR-jgvGFJQ"
    headers['Authorization'] = datapv.Library().get_token()
    # headers['Authorization'] = 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4MTIyYTNkMy1lZmQ2LTQwMjYtOGVlZi04MzMzNmJlNmFkNzciLCJpc3MiOiJzaG9ydGVzdHRyYWNrLXVhYSIsImF1dGhvcml0aWVzIjpbIlJPTEVfQ09NUEFOWV9BRE1JTiJdLCJkamFuZ29Vc2VySWQiOiI5OTkiLCJjbGllbnRfaWQiOiJ3ZWJfYXBwIiwiYXVkIjoid2ViX2FwcCIsImNvbXBhbnlJZCI6InRlc3Rfc2hvcnRlc3R0cmFja19mdW5jdGlvbmFsaXR5IiwiZGphbmdvVG9rZW4iOiI5NjUxYmQzZGJiZWExZDQ5YjM1MzhjZjRjMDU1MWMzODhiOGVlNzZlIiwic2NvcGUiOlsib3BlbmlkIl0sImV4cCI6MTUxNTg3MTg4MCwiaWF0IjoxNTE1NTcxODgwLCJqdGkiOiIwNzA5ZGMwZi0yMDNiLTRmOTQtYjliZS1iMjg1ZjAxZGNjOGEiLCJlbWFpbCI6InB1YmxpYy1hZG1pbkBsb2NhbGhvc3QifQ.cUmuy802LTcBzMeBxclH2QrTQkB6vjCvdqFdkYgDYuBZ_vC8ssxPubUl2_sUJLdhZGVuPMdJRYYNZ99iBdreEotOYo_npil0cS4CmuxgRobKGR5j6b6ZoHQHMyNjrmQXBHCfEdaxM56_J-FZ5_FwjmS3lacSV3ws7KB9mf7T4snUlTOH94XQb3njPCBkfqgp5yewMmB1xkwYQx7NHfC_ZOfsxrmPDyC1MfPuwIhB42e6s1K7OFWcgOkglD8mNCKQJY5gxAjl3HbjJwA_acgAd67t3c4QBhihuLGQFDgoY5ZbjkY5-kk7GspyTqKO63d_eI9qyR7JmSQBEAaZlNlG0A'
    # Add querystring to the URL if there are any arguments.
    if args is not None:
      qs = urllib.parse.urlencode(args)
      url = url + '?' + qs

    # Setup method to POST if unspecified, and appropriate request headers
    # if there is data to be sent within the request.
    if data is not None:
      if method is None:
        method = 'POST'

      if data != '':
        # If there is a content type specified, use it (and the data) as-is.
        # Otherwise, assume JSON, and serialize the data object.
        if 'Content-Type' not in headers:
          data = json.dumps(data)
          headers['Content-Type'] = 'application/json'
      headers['Content-Length'] = str(len(data))
    else:
      if method == 'POST':
        headers['Content-Length'] = '0'

    # If the method is still unset, i.e. it was unspecified, and there
    # was no data to be POSTed, then default to GET request.
    if method is None:
      method = 'GET'

    http = Http.http

    # Authorize with credentials if given.
#     if credentials is not None:
#       # Make a copy of the shared http instance before we modify it.
#       http = copy.copy(http)
#       http = google_auth_httplib2.AuthorizedHttp(credentials)
    if stats is not None:
      stats['duration'] = datetime.datetime.utcnow()

    response = None
    try:
      log.debug('request: method[%(method)s], url[%(url)s], body[%(data)s]' % locals())
      status_code = None
      if sys.version > '3':
        import requests
        if method == 'POST':
          response = requests.post(url=url, headers=headers, data=data)
          content = response.text
          status_code = response.status_code
        elif method == 'GET':
          response = requests.get(url=url, headers=headers)
          content = response.text
          status_code = response.status_code
      else:
        response, content = http.request(url,
                                         method=method,
                                         body=data,
                                         headers=headers)
        status_code = response.status

      if 200 <= status_code < 300:
        if raw_response:
          return content
        if type(content) == str:
          return json.loads(content)
        if content.strip()=='':
          return content
        else:
          return json.loads(str(content, encoding='UTF-8'))
      else:
        raise RequestException(response.status, content)
    except ValueError:
      raise Exception('Failed to process HTTP response.')
    except httplib2.HttpLib2Error:
      raise Exception('Failed to send HTTP request.')
    finally:
      if stats is not None:
        stats['data_size'] = len(data)
        stats['status'] = response.status
        stats['duration'] = (datetime.datetime.utcnow() - stats['duration']).total_seconds()
