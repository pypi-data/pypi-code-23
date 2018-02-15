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

"""Implements BigQuery HTTP API wrapper."""
from __future__ import absolute_import
from __future__ import unicode_literals

import time
from builtins import object

from st_library.dataprovider import _http


class Api(object):
  """A helper class to issue BigQuery HTTP requests."""

  # TODO(nikhilko): Use named placeholders in these string templates.
  # _ENDPOINT = 'https://shortesttrack.com'
  _METADATA_ENDPOINT = 'https://shortesttrack.com'
  _DATA_ENDPOINT = 'https://shortesttrack.com'
  _FILE_DOWNLOAD_PATH = '/api/data/blob-repositories/%s/download?name=%s'
  _FILE_DELETE_PATH = '/api/data/blob-repositories/%s?name=%s'
  _FILE_UPLOAD_PATH = '/api/data/blob-repositories/%s?name=%s'

  _DEFAULT_TIMEOUT = 60000


  def __init__(self):
    """Initializes the BigQuery helper with context information.

    """


  def tables_get(self, table_name, matrices_id):
    """Issues a request to retrieve information about a table.

    Args:
      table_name: a tuple representing the full name of the table.
    Returns:
      A parsed result object.
    Raises:
      Exception if there is an error performing the operation.
    """
    url = Api._METADATA_ENDPOINT + (Api._METADATA_MATRICES_PATH % matrices_id)
    return _http.Http.request(url)

  def download_object(self, datasetsid, file_name):
    """ Download an object.

    Args:
      datasetsid: the id of the dataset.
      file_name: the name of the dataset files.
    Returns:
      A url for downloading object.
    Raises:
      Exception if there is an error performing the operation.
    """
    url = Api._DATA_ENDPOINT + (Api._FILE_DOWNLOAD_PATH % (datasetsid, file_name))
    download_url = _http.Http.request(url, raw_response=True)
    return _http.Http.request(download_url, raw_response=True)

  def upload_object(self, datasetsid, file_name):
    """ Upload file to gcs.

    Args:
      file_name: the name of the file.
    Returns:
      A result object.
    Raises:
      Exception if there is an error performing the operation.
    """
    url = Api._DATA_ENDPOINT + (Api._FILE_UPLOAD_PATH % (datasetsid, file_name))

    filepath1 = file_name
    boundary = '----------%s' % hex(int(time.time() * 1000))
    data = []
    data.append('--%s' % boundary)
    fr1 = open(filepath1, 'rb')
    data.append('Content-Disposition: form-data; name="metadata"; filename="'+file_name+'"')
    data.append('Content-Type: %s\r\n' % 'application/json')
    data.append(fr1.read())
    fr1.close()

    data.append('--%s--\r\n' % boundary)

    http_body = '\r\n'.join(data)

    headers = {}
    headers['Content-Type'] = 'multipart/form-data; boundary=%s' % boundary

    return _http.Http.request(url=url, data=http_body, headers=headers, method='POST')

  def delete_object(self, datasetsid, file_name):
    """ Delete an object.

    Args:
      datasetsid: the id of the dataset.
      file_name: the name of the dataset files.
    Returns:
      A url for downloading object.
    Raises:
      Exception if there is an error performing the operation.
    """
    url = Api._DATA_ENDPOINT + (Api._FILE_DELETE_PATH % (datasetsid, file_name))
    return  _http.Http.request(url=url, method='DELETE')

