################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################
import sys
from watson_machine_learning_client.log_util import get_logger
from os.path import join as path_join
from pip import get_installed_distributions

for x in get_installed_distributions():
    if (x.project_name == 'watson-machine-learning-client'):
        sys.path.insert(1, path_join(x.location, 'watson_machine_learning_client', 'libs'))

from repository_v3.mlrepositoryclient import MLRepositoryClient
from watson_machine_learning_client.experiments import Experiments
from watson_machine_learning_client.training import Training
from watson_machine_learning_client.repository import Repository
from watson_machine_learning_client.instance import ServiceInstance
from watson_machine_learning_client.deployments import Deployments
from watson_machine_learning_client.utils import get_ml_token
from watson_machine_learning_client.wml_client_error import NoWMLCredentialsProvided

"""
.. module:: WatsonMachineLearningAPIClient
   :platform: Unix, Windows
   :synopsis: Watson Machine Learning API Client.

.. moduleauthor:: IBM
"""


class WatsonMachineLearningAPIClient:

    def __init__(self, wml_credentials):
        self._logger = get_logger(__name__)
        if wml_credentials is None:
            raise NoWMLCredentialsProvided()
        self.wml_credentials = wml_credentials
        self.wml_token, self._ml_repository_client = self._connect()
        self.service_instance = ServiceInstance(self.wml_credentials, self.wml_token)
        self.instance_details = self.service_instance.get_details()
        self.repository = Repository(self, self.wml_credentials, self.wml_token, self._ml_repository_client,
                                     self.instance_details)
        self.deployments = Deployments(self, self.wml_credentials, self.wml_token, self.instance_details)
        #self.training = Training(self, self.wml_credentials, self.wml_token, self.instance_details)
        #self.experiments = Experiments(self, self.wml_credentials, self.wml_token, self.instance_details)
        self._logger.info("Client successfully initialized")
        self.version = self._version()

    def _connect(self):
        if self.wml_credentials is not None:
            _ml_repository_client = MLRepositoryClient(self.wml_credentials['url'])

            _ml_repository_client.authorize(self.wml_credentials['username'],
                                           self.wml_credentials['password'])

            wml_token = get_ml_token(self.wml_credentials)
            self._logger.info("Successfully prepared token: " + wml_token)
            return wml_token, _ml_repository_client
        else:
            raise NoWMLCredentialsProvided()

    @staticmethod
    def _version():
        version = [pkg.version for pkg in get_installed_distributions() if pkg.project_name == 'watson-machine-learning-client'][0]

        return version
