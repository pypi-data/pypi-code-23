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
import st_library.dataprovider as datapv
import time

class Api(object):
  """A helper class to issue BigQuery HTTP requests."""

  # _ENDPOINT = 'https://shortesttrack.com'
  _METADATA_ENDPOINT = 'https://shortesttrack.com'
  _DATA_ENDPOINT = 'https://shortesttrack.com'
  _METADATA_MATRICES_PATH = '/api/metadata/matrices/%s'
  _DATA_GET_PATH = '/api/data/datasets/%s/matrices/%s/data'
  _DATA_SEC_GET_PATH = '/api/data/script-execution-configurations/%s/datasets/%s/matrices/%s/data'
  _PARAMETER_GET_PATH = '/api/metadata/script-execution-configurations/%s'
  _DATA_UPLOAD_PATH = '/api/data/datasets/%s/matrices/%s/upload'
  _DATA_INSERT_PATH = '/api/data/datasets/%s/matrices/%s/insert'
  _DATA_SEC_INSERT_PATH = '/api/data/script-execution-configurations/%s/datasets/%s/matrices/%s/insert'
  _DATA_SEC_BATCH_INSERT_PATH = '/api/data/script-execution-configurations/%s/datasets/%s/matrices/%s/upload'

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

  def tabledata_list(self, ifsec, datasetsid, table_name, start_index=None, max_results=None, page_token=None):
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
    if ifsec:
        configurationid = datapv.Library().get_config_id()
        url = Api._DATA_ENDPOINT + (Api._DATA_SEC_GET_PATH % (configurationid, datasetsid, table_name))
    else:
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

  def insert_sec_data(self, datasetsid, table_name, json_data):
    """ Insert streams data into matrix.

    Args:
      file_name: the name of the table as a tuple of components.
    Returns:
      A result object.
    Raises:
      Exception if there is an error performing the operation.
    """
    configurationid = datapv.Library().get_config_id()
    url = Api._DATA_ENDPOINT + (Api._DATA_SEC_INSERT_PATH % (configurationid, datasetsid, table_name))
    return _http.Http.request(url=url, data=json_data, method='POST')

  def insert_batch_sec_data(self, datasetsid, table_name, file_path, file_name):
    """ Insert streams data into matrix.

    Args:
      file_name: the name of the table as a tuple of components.
    Returns:
      A result object.
    Raises:
      Exception if there is an error performing the operation.
    """
    configurationid = datapv.Library().get_config_id()
    url = Api._DATA_ENDPOINT + (Api._DATA_SEC_BATCH_INSERT_PATH % (configurationid, datasetsid, table_name))

    metadata_file = '/home/st/workspace/dataprovider-py/samples/data/structured_data/metadata_sec.json'
    data_file = file_path+file_name
    boundary = '----------%s' % hex(int(time.time() * 1000))
    data = []
    data.append('--%s' % boundary)
    fr1 = open(metadata_file, 'rb')
    data.append('Content-Disposition: form-data; name="%s"; filename="metadata_sec.json"' % 'metadata')
    data.append('Content-Type: %s\r\n' % 'application/json')
    data.append(fr1.read())
    fr1.close()
    data.append('--%s' % boundary)
    fr2 = open(data_file, 'rb')
    data.append('Content-Disposition: form-data; name="%s"; filename="data.csv"' % 'data')
    data.append('Content-Type: %s\r\n' % 'application/vnd.ms-excel')
    data.append(fr2.read())
    fr2.close()
    data.append('--%s--\r\n' % boundary)

    http_body = '\r\n'.join(data)

    headers = {}
    headers['Content-Type'] = 'multipart/form-data; boundary=%s' % boundary

    return _http.Http.request(url=url, data=http_body, headers=headers, method='POST')

    # if sys.version > '3':
    #   from requests_toolbelt.multipart.encoder import MultipartEncoder
    #
    #   multipart_data = MultipartEncoder(
    #     fields={
    #       'metadata':('metadata_sec.json',
    #                open('/home/st/workspace/dataprovider-py/samples/data/structured_data/metadata_sec.json',
    #                     'rb'), 'text/plain'),
    #       # a file upload field
    #       'data': (file_name,
    #                open(file_path+file_name,
    #                     'rb'), 'text/plain')
    #     }
    #   )
    #   headers = {}
    #   headers['Content-Type'] = multipart_data.content_type
    #
    #   return _http.Http.request(url=url, data=multipart_data, headers=headers, method='POST')
    # else:
    #   from poster.encode import multipart_encode
    #   from poster.streaminghttp import register_openers
    #
    #   # Register the streaming http handlers with urllib2
    #   register_openers()
    #
    #   # Start the multipart/form-data encoding of the file
    #   # "file" is the name of the parameter, which is normally set
    #   # via the "name" parameter of the HTML <input> tag.
    #   # headers contains the necessary Content-Type and Content-Length
    #   # datagen is a generator object that yields the encoded parameters
    #   datagen, headers = multipart_encode(
    #     {"metadata": open('/home/st/workspace/dataprovider-py/samples/data/structured_data/metadata_sec.json','rb'),"data": open(file_path+file_name,'rb')})
    #
    #   return _http.Http.request(url=url, data=datagen, headers=headers, method='POST')
