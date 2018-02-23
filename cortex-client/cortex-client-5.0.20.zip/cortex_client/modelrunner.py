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
import copy
import json
from typing import Dict, Union
from urllib.parse import urlparse

from .cache import CacheHandler
from .datasetsclient import build_datasetsclient
from .modelclient import build_modelclient
from .types import InputMessage, Model
from .modelprocess import ModelProcess
from .modelclient import ModelClient

class ModelRunner:
    """The ModelRunner is responsible for executing the ModelProcessor 
    implementation, and storing and retrieving execution artifacts.
    """

    def __init__(self, modelprocess: ModelProcess) -> None:
        self.modelprocess = modelprocess
        # TODO: parameterize cache path:
        self.cache = CacheHandler('/tmp/cortex')

    ## Public ##

    def run_train(self, context: InputMessage):
        """Runs the ModelProcess.train function

        :param context: a Cortex InputMessage.
        """
        dataset_client = build_datasetsclient(context)
        model_client   = build_modelclient(context)
        model = model_client.create_model_version(context.instance_id, 
                                                  context.channel_id, 
                                                  self.modelprocess.name, 
                                                  self.modelprocess.__doc__ or \
                                                  self.modelprocess.name)

        model_client.log_train_status(model, 'started')

        request_args = self._prepare_request_args(context)
        data = self.modelprocess.fetch_training_data(request_args, dataset_client)
        trained_model = self.modelprocess.train(request_args, data, model, model_client)
        for k,v in trained_model.items():
            model_client.save_state(model, k, self.modelprocess.serialize(k, v))
        model_client.log_train_status(model, 'complete')
        return model._id

    def run_inquire(self, context: InputMessage):
        """Runs the ModelProcess.inquire function

        :param context: a Cortex InputMessage.
        """
        model_client   = build_modelclient(context)
        print("Getting serliazlied model...")
        model = model_client.get_model(context.instance_id, 
                                       context.channel_id, 
                                       self.modelprocess.name,
                                       'latest')
        des_items = self._get_deserialized_trained_model(model, model_client)
        request_args = self._prepare_request_args(context)
        return self.modelprocess.inquire(request_args, des_items, model, model_client)

    ## Private ##

    def _load_state_and_cache(self, model_client: ModelClient, model: Model, k: str) -> bytes:
        ## TODO: load_state should not call read() and should support stream.
        data  = self.cache.load_state(model, k) or model_client.load_state(model, k).read()
        self.cache.save_state(model, k, data)
        return data

    def _get_deserialized_trained_model(self, model: Model, model_client: ModelClient) -> Dict[str, object]:
        deserialized_items = {}
        for k in self.modelprocess.get_model_keys_for_serving():
            ser_item = self._load_state_and_cache(model_client, model, k)
            item = self.modelprocess.deserialize(k, ser_item)
            deserialized_items[k] = item
        return deserialized_items

    @staticmethod
    def _prepare_request_args(input_message: InputMessage) -> Dict[str, object]:
        def hydrate_values(dic: Dict[str, Union[str, bytes, bytearray]]) -> Dict[str, object]:
            ## This is ugly, but Cortex 5 properties can not be nested (JSON), 
            ## so they need to be encoded as strings.
            result = {}
            for k, v in dic.items():
                try:
                    result[k] = json.loads(v)
                except (json.decoder.JSONDecodeError, TypeError):
                    result[k] = v
            return result
        payload = input_message.payload.copy()
        properties = input_message.properties.copy()
        result = hydrate_values(properties)
        result.update(payload)
        return result
