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
import abc
from typing import Dict, List

from .datasetsclient import DatasetsClient
from .modelclient import ModelClient
from .types import Model

class ModelProcess(metaclass=abc.ABCMeta):

    # the name of the Model. 
    # Used by the ModelRunner to label the Cortex Model. 
    name = None 

    @staticmethod
    def get_model_keys_for_serving() -> List[str]:
        """Returns a list of keys (strings) corresponding to the items needed 
        during inquiry that are serialized by `train`.
        """
        raise NotImplementedError()

    @staticmethod
    @abc.abstractmethod
    def fetch_training_data(request: Dict[str, object], datasets_client: DatasetsClient) -> object:
        """Gets training data using the `DatasetsClient`

        :param request: The arguments passed from the request to train.
        :param datasets_client: The DatasetsClient to fetch training data 
            from Cortex.

        :return: The training data.
        """
        raise NotImplementedError()

    @staticmethod
    @abc.abstractmethod
    def train(request: Dict[str, object], 
              data: object, 
              cortex_model: Model, 
              client: ModelClient) -> Dict[str, object]:
        """Perform training of the Model. 

        :param request: The arguments needed to train the model.
        :param data: The training data.
        :param cortex_model: The Cortex Model object with which this train is 
            associated. This sould be used with the ModelClient to log Model events.
        :param client: The ModelClient with methods to log training events.

        :return: A dictionary of serializable objects, ready to be persisted in Cortex
        """
        raise NotImplementedError()

    @staticmethod
    @abc.abstractmethod
    def inquire(request: Dict[str, object], 
                trained_model: object, 
                cortex_model: Model, 
                client: ModelClient) -> object:
        """Performs ask against a `trained_model`. 

        :param request: The arguments from the end user to perform inquiry.
        :param trained_model: The trained model to use for the inquiry.
        :param cortex_model: The Cortex Model object with which this train is 
            associated. This sould be used with the ModelClient to log Model events.
        :param client: The ModelClient with methods to log training events.

        :return: The inquiry result.
        """
        raise NotImplementedError()

    @staticmethod
    @abc.abstractmethod
    def serialize(key: str, datum: object) -> bytes:
        """Serializes ``datum`` for the given ``key``. 
        This ModelProcess should define it's method to serialize/deserialize
        different pieces of data.

        :param key: A string identifying the ``datum``. 
        :param datum: An object to be serialized.

        :return: A serialized object.
        """
        raise NotImplementedError()

    @staticmethod
    @abc.abstractmethod
    def deserialize(key: str, datum: bytes) -> object:
        """Deserialized a ``datum`` for the given ``key`` identifier. 

        :param key: A string identifying the ``datum``. 
        :param datum: An object to be de-serialized.

        :return: A de-serialized object.
        """
        raise NotImplementedError()
