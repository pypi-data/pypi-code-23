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
from .types import Model, JSONType

class ModelProcess(metaclass=abc.ABCMeta):

    # the name of the Model. 
    # Used by the ModelRunner to label the Cortex Model. 
    name = None 

    @staticmethod
    @abc.abstractmethod
    def train(request: Dict[str, object], 
              cortex_model: Model, 
              datasets_client: DatasetsClient,
              model_client: ModelClient) -> None:
        """Perform training of the Model. 

        :param request: The arguments needed to train the model.
        :param cortex_model: The Cortex Model object with which this train is 
        :param datasets_client: The DatasetsClient to download training data.
        :param model_client: The ModelClient with methods to report training events.
        """
        raise NotImplementedError()

    @staticmethod
    @abc.abstractmethod
    def inquire(request: Dict[str, object], 
                cortex_model: Model, 
                model_client: ModelClient) -> JSONType:
        """Performs ask against a `trained_model`. 

        :param request: The arguments from the end user to perform inquiry.
        :param cortex_model: The Cortex Model object with which this train is 
            associated. This sould be used with the ModelClient to log Model events.
        :param model_client: The ModelClient with methods to log training events.

        :return: The inquiry result.
        """
        raise NotImplementedError()

    # @staticmethod
    # @abc.abstractmethod
    # def inquire_init(cortex_model: Model, model_client: ModelClient) -> JSONType:
        # raise NotImplementedError()
