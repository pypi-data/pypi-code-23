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
from datetime import datetime
import io
import json
import os
from typing import Dict, Union
from urllib.parse import urlparse
from urllib3.response import HTTPResponse

from .authenticationclient import AuthenticationClient
from .cache import CacheHandler
from .client import build_client
from .config import Config
from .datasetsclient import DatasetsClient
from .serviceconnector import ServiceConnector
from .types import InputMessage, ModelEvent, Model
from .utils import get_logger

log = get_logger(__name__)

class ModelClient:

    URIs = {'models':           'models',
            'model_events':     'models/events',
            'model_versions':   'models/versions',
            'model_serialized': 'models/{}/serialized',
            'content':          'content'}

    def __init__(self, connection_config):
        self.config = connection_config
        self._serviceconnector = ServiceConnector(connection_config)
        self.cache = CacheHandler('/opt/ml')

    # TODO: should this return a Response or the object creted directly?
    def create_model_version(self, agent_id, processor_id, name, description) -> Model:
        """Creates a new Model version to link with a training execution.

        :param agent_id: The unique id of the agent instance.
        :param processor_id: The unique id of the processor.
        :param name: The name of the new Model.
        :param description: An arbitrary textual description.

        :return: A Model object.
        """
        body    = {"agentId": agent_id, 
                   "processorId": processor_id, 
                   "name": name, 
                   "description": description}
        body_s  = json.dumps(body)
        headers = {'Content-Type': 'application/json'}
        response = self._serviceconnector.request('POST', self.URIs['models'], body_s, headers)
        response.raise_for_status()
        return Model._make(response.json())

    ## ModelEvent loggers ##

    def log_data_stats(self, model, value: object):
        """Before training, log stats about the data itself. (sync)

        :param model: A Model object against to log events.
        :param value: The value to log.
        """
        return self.log_event(model, 'cortex.train.data.stats', value)

    def log_hyperparams(self, model, value):
        """Log hyperparameters (sync) 

        :param model: A Model object against to log events.
        :param value: The value to log.
        """
        return self.log_event(model, 'cortex.train.hyperparameters', value)

    def log_train_progress(self, model, value: object):
        """Log training progress. (sync)

        :param model: A Model object against to log events.
        :param value: The value to show progress.
        """
        return self._log_train_status(model, {'progress': value})

    def log_serving_datum(self, model, label: str, value: object):
        """Log inquiry results. (sync/async)
        
        :param model: A Model object against to log events.
        :param label: An arbitrary label to attach  to the event key.
        :param value: The value to log.
        """
        return self.log_event(model, 'inquiry.' + label, value)

    def log_event(self, model, key: str, value: object):
        """Log an arbitrary / generic ModelEvent. (sync/async)
       
        :param model: A Model object against to log events.
        :param key: A string specifying the event type (e.g., cortex.train.status)
        :param value: The value to log.

        :return: a requests.Response object.
        """
        uri    = self.URIs['model_events']
        body   = ModelEvent(model._id, key, value, str(datetime.now()))
        body_s = json.dumps(body._asdict())
        headers = {'Content-Type': 'application/json'}
        return self._serviceconnector.request('POST', uri, body_s, headers)

    ## Data ##

    def get_model(self, agent_id, processor_id, name, version):
        """Gets the Cortex Model object.

        :param agent_id: The Agent instance ID of the Agent to which the Model belongs.
        :param processor_id: The ID of the processor to which the Model belongs.
        :param name: The name of the Model to retrieve.
        :param version: The version of the Model to retrieve.

        :return: A Model object.
        """
        uri = '/'.join([self.URIs['model_versions'], agent_id, processor_id, name, version])
        r = self._serviceconnector.request('GET', uri)
        r.raise_for_status()
        return Model._make(r.json())

    def get_model_id(self, agent_id, processor_id, name, version):
        """Returns the unique ID of a Model."""
        return self.get_model(agent_id, processor_id, name, version)._id

    def get_serialized_model_refs(self, model_id):
        uri = self.URIs['model_serialized'].format(model_id)
        r = self._serviceconnector.request('GET', uri)
        r.raise_for_status()
        return r.json()

    ## TODO: What should be the file path in Minio/S3?
    ## (cortex-content) /<tenant>/models/<processorname>/<agent id>/<processor ref id>/<model version>/<filename>
    def upload_state(self, model, key: str, stream: object) -> object:
        """Upload a Trained Model. (sync)
        
        :param model: The Model object associated with the serialized trained model to store.
        :param key: The path where the serialized model will be stored.
        :param value: The actual payload (serialized model) to store.

        :return: requests.Response
        """
        log.info('Uploading state with key "{}" for model "{}..."'.format(key, model.name))
        client = DatasetsClient(self.config)
        coord = model._construct_serialized_model_path(key)
        r = client.upload(coord, 'model', stream, 'application/octet-stream')
        self._log_serialized_model_refs(model, {key: coord})
        log.info('Uploaded saved.')
        return r

    def download_state(self, model: Model, key: str) -> HTTPResponse:
        """Download the persisted model.

        :param model: The Model object from which to retrieve an artifact (e.g., serialized model)
        :param key: the path / name of the object to retrieve.

        :return: The content of a request.Response object.
        """
        client = DatasetsClient(self.config)
        coord = model._construct_serialized_model_path(key)
        return client.download(coord)

    def save_state(self, model, key: str, stream):
        """Save a Trained Model. (sync)
        
        :param model: The Model object associated with the serialized trained model to store.
        :param key: The path where the serialized model will be stored.
        :param value: The actual payload (serialized model) to store.

        :return: requests.Response
        """
        return self.upload_state(model, key, stream)

    def load_state(self, model: Model, key: str):
        """Returns the persisted model.

        :param model: The Model object from which to retrieve an artifact (e.g., serialized model)
        :param key: the path / name of the object to retrieve.

        :return: The content of a request.Response object.
        """
        return self.load_state_cache(model, key) or \
               self.download_state(model, key)


    def save_state_cache(self, model: Model, key: str, stream: Union[bytes, io.BufferedReader]):
        """Save a Trained Model to disk.

        :param model: The Model object associated with the serialized trained model to store.
        :param key: The path where the serialized model will be stored.
        :param stream: The serialized model to store.

        """
        key = model._construct_serialized_model_path(key)
        return self.cache.save_state(model, key, stream)

    def load_state_cache(self, model: Model, key: str):
        """Read the persisted model from disk cache.

        :param model: The Model object from which to retrieve an artifact (e.g., serialized model)
        :param key: the path / name of the object to retrieve.
        """
        key = model._construct_serialized_model_path(key)
        return self.cache.load_state(model, key)

    ## Private ##

    def _log_serialized_model_refs(self, model: Model, value: Dict[str, str]):
        return self.log_event(model, 'cortex.train.model', value)

    def _log_train_status(self, model, value):
        """Log training status. (sync)

        :param model: A Model object against to log events.
        :param value: The value to log.
        """
        return self.log_event(model, 'cortex.train.status', value)


def build_modelclient(input_message: InputMessage) -> ModelClient:
    """A ModelClient constructor function.

    :param input_message: the Cortex InputMessage containing all the constructor parameters.

    :return: ModelClient
    """
    return build_client(ModelClient, input_message)
