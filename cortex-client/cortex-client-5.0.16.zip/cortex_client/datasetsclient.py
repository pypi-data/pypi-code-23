"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import json
from typing import Dict
from urllib.parse import urlparse

from requests_toolbelt.multipart.encoder import MultipartEncoder

from .authenticationclient import AuthenticationClient
from .config import Config
from .serviceconnector import ServiceConnector
from .types import InputMessage
from .client import build_client

class DatasetsClient:

    URIs = {'datasets': 'datasets',
            'content':  'content'}

    def __init__(self, connection_config):
        self._serviceconnector = ServiceConnector(connection_config)

    def save_dataset(self, dataset: Dict[str, object]):
        """Saves a Dataset.
        
        :param dataset: a Cortex Dataset as dict.
        """
        uri = self.URIs['datasets']
        body_s = json.dumps(dataset)
        headers = {'Content-Type': 'application/json'}
        r = self._serviceconnector.request('POST', uri, body_s, headers)
        r.raise_for_status()
        return r.json()

    def get_dataframe(self, dataset_name: str):
        """Gets data from a dataset as a dataframe.

        :param dataset_name: the name of the dataset to pull data from.

        :return: a dataframe dictionary.
        """
        uri = '/'.join([self.URIs['datasets'], dataset_name, 'dataframe'])
        r = self._serviceconnector.request('GET', uri)
        r.raise_for_status()
        return r.json()

    ## Content ##

    def upload(self, key, stream, content_type):
        """Store `stream` file in S3.

        :param key: the path where the file will be stored.
        :param stream: the file object.
        :param content_type: the type of the file to store (e.g., `text/csv`)

        :return: a dict with the response to request upload. 
        """
        uri  = self.URIs['content']
        fields = {'key': key, 
                  'content': ('model', stream, content_type)}
        data = MultipartEncoder(fields=fields)
        headers = {'Content-Type': data.content_type}
        r = self._serviceconnector.request('POST', uri, data, headers)
        r.raise_for_status()
        return r.json()


def build_datasetsclient(input_message: InputMessage) -> DatasetsClient:
    return build_client(DatasetsClient, input_message)
