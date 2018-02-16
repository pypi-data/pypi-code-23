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
from st_library.dataprovider import _http
import time

class Api(object):
  """A helper class to issue BigQuery HTTP requests."""

  # _ENDPOINT = 'https://shortesttrack.com'
  _METADATA_ENDPOINT = 'https://shortesttrack.com'
  _DATA_ENDPOINT = 'https://shortesttrack.com'
  _METADATA_MATRICES_PATH = '/api/metadata/matrices/%s'
  _DATA_GET_PATH = '/api/data/datasets/%s/matrices/%s/data'
  _PARAMETER_GET_PATH = '/api/metadata/script-execution-configurations/%s'
  _DATA_UPLOAD_PATH = '/api/data/datasets/%s/matrices/%s/upload'
  _DATA_INSERT_PATH = '/api/data/datasets/%s/matrices/%s/insert'

  _DEFAULT_TIMEOUT = 60000


  def __init__(self):
    """Initializes the BigQuery helper with context information.

    """


  def tables_get(self, matrices_id):
    """Issues a request to retrieve information about a table.

    Args:
      matrices_id: .
    Returns:
      A parsed result object.
    Raises:
      Exception if there is an error performing the operation.
    """
    url = Api._METADATA_ENDPOINT + (Api._METADATA_MATRICES_PATH % matrices_id)
    return _http.Http.request(url)

  def tables_get_parameter(self, script_id):
    """Issues a request to retrieve the parameter of the script execution configuration.

    Args:
      script_id:
    Returns:
      A parsed result object.
    Raises:
      Exception if there is an error performing the operation.
    """
    url = Api._METADATA_ENDPOINT + (Api._PARAMETER_GET_PATH % script_id)
    return _http.Http.request(url)

  def tabledata_list(self, datasetsid, table_name, start_index=None, max_results=None, page_token=None):
    """ Retrieves the contents of a table.

    Args:
      table_name: the name of the table as a tuple of components.
      start_index: the index of the row at which to start retrieval.
      max_results: an optional maximum number of rows to retrieve.
      page_token: an optional token to continue the retrieval.
    Returns:
      A parsed result object.
    Raises:
      Exception if there is an error performing the operation.
    """
    url = Api._DATA_ENDPOINT + (Api._DATA_GET_PATH % (datasetsid, table_name))
    args = {}
    if start_index:
      args['startIndex'] = start_index
    if max_results:
      args['maxResults'] = max_results
    if page_token is not None:
      args['pageToken'] = page_token
    return _http.Http.request(url, args=args)

  def tabledata_post(self, datasetsid, table_name, file_name):
    """ Insert the contents of a table.

    Args:
      file_name: the name of the table as a tuple of components.
    Returns:
      A result object.
    Raises:
      Exception if there is an error performing the operation.
    """
    url = Api._DATA_ENDPOINT + (Api._DATA_UPLOAD_PATH % (datasetsid, table_name))

    filepath1 = r"/home/st/workspace/st-dataprovider-python/datalab/structured_data/metadata.json"
    filepath2 = file_name
    boundary = '----------%s' % hex(int(time.time() * 1000))
    data = []
    data.append('--%s' % boundary)
    fr1 = open(filepath1, 'rb')
    data.append('Content-Disposition: form-data; name="%s"; filename="metadata.json"' % 'metadata')
    data.append('Content-Type: %s\r\n' % 'application/json')
    data.append(fr1.read())
    fr1.close()
    data.append('--%s' % boundary)
    fr2 = open(filepath2, 'rb')
    data.append('Content-Disposition: form-data; name="%s"; filename="data.csv"' % 'file')
    data.append('Content-Type: %s\r\n' % 'application/vnd.ms-excel')
    data.append(fr2.read())
    fr2.close()
    data.append('--%s--\r\n' % boundary)

    http_body = '\r\n'.join(data)

    headers = {}
    headers['Content-Type'] = 'multipart/form-data; boundary=%s' % boundary

    return _http.Http.request(url=url, data=http_body, headers=headers, method='POST')

  def insert_data(self, datasetsid, table_name, json_data):
    """ Insert streams data into matrix.

    Args:
      file_name: the name of the table as a tuple of components.
    Returns:
      A result object.
    Raises:
      Exception if there is an error performing the operation.
    """
    url = Api._DATA_ENDPOINT + (Api._DATA_INSERT_PATH % (datasetsid, table_name))
    return _http.Http.request(url=url, data=json_data, method='POST')
