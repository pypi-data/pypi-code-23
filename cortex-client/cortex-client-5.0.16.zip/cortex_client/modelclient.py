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
from collections import namedtuple
from urllib.parse import urlparse
import json
from typing import Dict

from .authenticationclient import AuthenticationClient
from .config import Config
from .serviceconnector import ServiceConnector
from .types import InputMessage, ModelEvent, Model
from .client import build_client


class ModelClient:

    URIs = {'models':         'models',
            'model_events':   'models/events',
            'model_versions': 'models/versions',
            'content':        'content'}

    def __init__(self, connection_config):
        self._serviceconnector = ServiceConnector(connection_config)

    # TODO: should this return a Response or the object creted directly?
    def create_model_version(self, agentId, processorId, name, description) -> Model:
        """Creates a new Model version to link with a training execution.

        :param agentId: The unique id of the agent instance.
        :param processorId: The unique id of the processor.
        :param name: The name of the new Model.
        :param description: An arbitrary textual description.

        :return: A Model object.
        """
        body    = {"agentId": agentId, 
                   "processorId": processorId, 
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
        return self.log_event(model, 'train.data.stats', value)

    def log_hyperparams(self, model, value):
        """Log hyperparameters (sync) 

        :param model: A Model object against to log events.
        :param value: The value to log.
        """
        return self.log_event(model, 'train.hyperparameters', value)

    def log_train_progress(self, model, value):
        """Log training progress status. (sync)

        :param model: A Model object against to log events.
        :param value: The value to log.
        """
        return self.log_event(model, 'train.progress', value)

    def log_serving_datum(self, model, label: str, value: object):
        """Log inquiry results. (sync/async)
        
        :param model: A Model object against to log events.
        :param label: An arbitrary label to attach  to the event key.
        :param value: The value to log.
        """
        return self.log_event(model, 'inquiry.' + label, value)

    def log_serialized_model_refs(self, model: Model, value: Dict[str, str]):
        return self.log_event(model, 'train.model', value)

    def log_event(self, model, key: str, value: object):
        """Log an arbitrary / generic ModelEvent. (sync/async)
       
        :param model: A Model object against to log events.
        :param key: A string specifying the event type (e.g., train.progress)
        :param value: The value to log.

        :return: a requests.Response object.
        """
        uri    = self.URIs['model_events']
        body   = ModelEvent(model._id, key, value)
        body_s = json.dumps(body._asdict())
        headers = {'Content-Type': 'application/json'}
        return self._serviceconnector.request('POST', uri, body_s, headers)

    ## Data ##

    def get_model(self, agentId, processorId, name, version):
        """Gets the Cortex Model object.

        :param agentId: The Agent instance ID of the Agent to which the Model belongs.
        :param processorId: The ID of the processor to which the Model belongs.
        :param name: The name of the Model to retrieve.
        :param version: The version of the Model to retrieve.

        :return: A Model object.
        """
        uri = '/'.join([self.URIs['model_versions'], agentId, processorId, name, version])
        r = self._serviceconnector.request('GET', uri)
        r.raise_for_status()
        return Model._make(r.json())

    def get_model_id(self, agentId, processorId, name, version):
        """Returns the unique ID of a Model."""
        return self.get_model(agentId, processorId, name, version)._id

    ## TODO: What should be the file path in Minio/S3?
    ## (cortex-content) /<tenant>/models/<processorname>/<agent id>/<processor ref id>/<model version>/<filename>
    def save_state(self, model, key: str, value: object) -> object:
        """Save a Trained Model. (sync)
        
        :param model: The Model object associated with the serialized trained model to store.
        :param key: The path where the serialized model will be stored.
        :param value: The actual payload (serialized model) to store.

        :return: requests.Response
        """
        uri   = self.URIs['content']
        coord = self._construct_serialized_model_path(model._id, model.name, key)
        data  = {'key': coord}
        files = {'content': value}
        file_r  = self._serviceconnector.post_file(uri, files, data, headers=None)
        self.log_serialized_model_refs(model, {key: coord})
        return file_r

    def load_state(self, model: Model, key: str) -> bytes:
        """Returns the persisted model.
        
        :param model: The Model object from which to retrieve an artifact (e.g., serialized model)
        :param key: the path / name of the object to retrieve.

        :return: The content of a request.Response object.
        """
        coord = self._construct_serialized_model_path(model._id, model.name, key)
        uri   = self.URIs['content'] + '/' + coord
        r = self._serviceconnector.request('GET', uri)
        r.raise_for_status()
        return r.content

    ## Private ##

    @staticmethod
    def _construct_serialized_model_path(modelUID, name, key):
        return '/'.join(['model', str(modelUID), str(name), str(key)])


def build_modelclient(input_message: InputMessage) -> ModelClient:
    """A ModelClient constructor function.

    :param input_message: the Cortex InputMessage containing all the constructor parameters.

    :return: ModelClient
    """
    return build_client(ModelClient, input_message)
