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

import sys

from st_library.dataprovider import _http


class Api(object):
  """A helper class to issue BigQuery HTTP requests."""
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

  def upload_object(self, datasetsid, file_name, file_path):
    """ Upload file to gcs.

    Args:
      file_name: the name of the file.
      file_path: the path of the file.
    Returns:
      A result object.
    Raises:
      Exception if there is an error performing the operation.
    """
    url = Api._DATA_ENDPOINT + (Api._FILE_UPLOAD_PATH % (datasetsid, file_name))

    if sys.version > '3':
      from requests_toolbelt.multipart.encoder import MultipartEncoder

      multipart_data = MultipartEncoder(
        fields={
          # a file upload field
          'file': (file_name,
                   open(file_path+file_name,
                        'rb'), 'text/plain')
        }
      )
      headers = {}
      headers['Content-Type'] = multipart_data.content_type

      return _http.Http.request(url=url, data=multipart_data, headers=headers, method='POST')
    else:
      from poster.encode import multipart_encode
      from poster.streaminghttp import register_openers

      # Register the streaming http handlers with urllib2
      register_openers()

      # Start the multipart/form-data encoding of the file
      # "file" is the name of the parameter, which is normally set
      # via the "name" parameter of the HTML <input> tag.
      # headers contains the necessary Content-Type and Content-Length
      # datagen is a generator object that yields the encoded parameters
      datagen, headers = multipart_encode(
        {"file": open(file_path+file_name)})
      return _http.Http.request(url=url, data=datagen, headers=headers, method='POST')

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

