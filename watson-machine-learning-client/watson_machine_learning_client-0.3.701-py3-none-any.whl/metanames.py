################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################
from repository_v3.mlrepository import MetaNames
from tabulate import tabulate
import json
from watson_machine_learning_client.wml_resource import WMLResource


class ExperimentMetaNames:
    """
    Set of Meta Names for experiments.

    Available MetaNames:

    +-----------------------------------------------+------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | MetaName                                      | Type | Required | Example value                                                                                                                                                                                                                                        |
    +===============================================+======+==========+======================================================================================================================================================================================================================================================+
    | ExperimentMetaNames.NAME                      | str  | Y        | ``"Hand-written Digit Recognition"``                                                                                                                                                                                                                 |
    +-----------------------------------------------+------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | ExperimentMetaNames.DESCRIPTION               | str  | N        | ``"Hand-written Digit Recognition training"``                                                                                                                                                                                                        |
    +-----------------------------------------------+------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | ExperimentMetaNames.AUTHOR_NAME               | str  | N        | ``"John Smith"``                                                                                                                                                                                                                                     |
    +-----------------------------------------------+------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | ExperimentMetaNames.AUTHOR_EMAIL              | str  | Y        | ``"John.Smith@x.x"``                                                                                                                                                                                                                                 |
    +-----------------------------------------------+------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | ExperimentMetaNames.OPTIMIZATION_METHOD       | str  | N        | ``"random"``                                                                                                                                                                                                                                         |
    +-----------------------------------------------+------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | ExperimentMetaNames.OPTIMIZATION_PARAMETERS   | json | N        | ``{}``                                                                                                                                                                                                                                               |
    +-----------------------------------------------+------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | ExperimentMetaNames.EVALUATION_METHOD         | str  | N        | ``"multiclass"``                                                                                                                                                                                                                                     |
    +-----------------------------------------------+------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | ExperimentMetaNames.EVALUATION_METRICS        | list | Y        | ``["accuracy"]``                                                                                                                                                                                                                                     |
    +-----------------------------------------------+------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | ExperimentMetaNames.TRAINING_REFERENCES       | json | Y        | ``[{"training_definition_url": "https://ibm-watson-ml.mybluemix.net/v3/ml_assets/training_definitions/12345"}, {"training_definition_url": "https://ibm-watson-ml.mybluemix.net/v3/ml_assets/training_definitions/67890"}]``         |
    +-----------------------------------------------+------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | ExperimentMetaNames.TRAINING_DATA_REFERENCE   | json | Y        | ``{"connection": {"endpoint_url": "https://s3-api.us-geo.objectstorage.softlayer.net", "access_key_id": "***", "secret_access_key": "***"}, "source": {"bucket": "train-data"}, "type": "s3"}``  |
    +-----------------------------------------------+------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | ExperimentMetaNames.TRAINING_RESULTS_REFERENCE| json | Y        | ``{"connection": {"endpoint_url": "https://s3-api.us-geo.objectstorage.softlayer.net", "access_key_id": "***", "secret_access_key": "***"}, "target": {"bucket": "result-data"}, "type": "s3"}`` |
    +-----------------------------------------------+------+----------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    """
    def __init__(self):
        self.NAME = "name"
        self.DESCRIPTION = "description"
        self.AUTHOR_NAME = "author_name"
        self.AUTHOR_EMAIL = "author_email"
        self.OPTIMIZATION_METHOD = "optimization_method"
        self.OPTIMIZATION_PARAMETERS = "optimization_method_parameters"
        self.EVALUATION_METHOD = "evaluation_method"
        self.EVALUATION_METRICS = "evaluation_metrics"
        self.TRAINING_REFERENCES = "training_references"
        self.TRAINING_DATA_REFERENCE = "training_data_reference"
        self.TRAINING_RESULTS_REFERENCE = "training_results_reference"

        self._NAME_REQUIRED = True
        self._DESCRIPTION_REQUIRED = False
        self._AUTHOR_NAME_REQUIRED = False
        self._AUTHOR_EMAIL_REQUIRED = True
        self._OPTIMIZATION_METHOD_REQUIRED = False
        self._OPTIMIZATION_PARAMETERS_REQUIRED = False
        self._EVALUATION_METHOD_REQUIRED = False
        self._EVALUATION_METRICS_REQUIRED = True
        self._TRAINING_REFERENCES_REQUIRED = True
        self._TRAINING_DATA_REFERENCE_REQUIRED = True
        self._TRAINING_RESULTS_REFERENCE_REQUIRED = True

    def _validate(self, meta_props):
        WMLResource._validate_meta_prop(meta_props, self.NAME, str, self._NAME_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.DESCRIPTION, str, self._DESCRIPTION_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.AUTHOR_NAME, str, self._AUTHOR_NAME_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.AUTHOR_EMAIL, str, self._AUTHOR_EMAIL_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.OPTIMIZATION_METHOD, str, self._OPTIMIZATION_METHOD_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.OPTIMIZATION_PARAMETERS, list, self._OPTIMIZATION_PARAMETERS_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.EVALUATION_METHOD, str, self._EVALUATION_METHOD_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.EVALUATION_METRICS, list, self._EVALUATION_METRICS_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.TRAINING_REFERENCES, object, self._TRAINING_REFERENCES_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.TRAINING_DATA_REFERENCE, object, self._TRAINING_DATA_REFERENCE_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.TRAINING_RESULTS_REFERENCE, object, self._TRAINING_RESULTS_REFERENCE_REQUIRED)

    def get(self):
        """
        Get available experiment metanames.

        :return: available experiment metanames
        :rtype: array
        """
        return sorted(list(filter(lambda x: not x.startswith('_'), self.__dict__.keys())))

    def show(self):
        """
        Shows possible metanames, type and if it is required.
        """
        table = tabulate(
            [
                ["META_PROP NAME",               "TYPE", "REQUIRED"],
                ["NAME",                         "str",  "Y" if self._NAME_REQUIRED else "N"],
                ["DESCRIPTION",                  "str",  "Y" if self._DESCRIPTION_REQUIRED else "N"],
                ["AUTHOR_NAME",                  "str",  "Y" if self._AUTHOR_NAME_REQUIRED else "N"],
                ["AUTHOR_EMAIL",                 "str",  "Y" if self._AUTHOR_EMAIL_REQUIRED else "N"],
                # ["OPTIMIZATION_METHOD",        "str",  "Y" if self._OPTIMIZATION_METHOD_REQUIRED else "N"],
                # ["OPTIMIZATION_PARAMETERS",    "json",  "Y" if self._OPTIMIZATION_PARAMETERS_REQUIRED else "N"],
                ["EVALUATION_METHOD",            "str",  "Y" if self._EVALUATION_METHOD_REQUIRED else "N"],
                ["EVALUATION_METRICS",           "list", "Y" if self._EVALUATION_METRICS_REQUIRED else "N"],
                ["TRAINING_REFERENCES",          "json", "Y" if self._TRAINING_REFERENCES_REQUIRED else "N"],
                ["TRAINING_DATA_REFERENCE",      "json", "Y" if self._TRAINING_DATA_REFERENCE_REQUIRED else "N"],
                ["TRAINING_RESULTS_REFERENCE",   "json", "Y" if self._TRAINING_RESULTS_REFERENCE_REQUIRED else "N"]
            ]
        )
        print(table)

    def get_example_values(self):
        """
        Get example values for metanames.

        :return: example meta_props
        :rtype: json
        """
        training_data_reference = {
            "connection": {
                "endpoint_url": "https://s3-api.us-geo.objectstorage.softlayer.net",
                "access_key_id": "***",
                "secret_access_key": "***"
            },
            "source": {
                "bucket": "train-data"
            },
            "type": "s3"
        }

        training_results_reference = {
            "connection": {
                "endpoint_url": "https://s3-api.us-geo.objectstorage.softlayer.net",
                "access_key_id": "***",
                "secret_access_key": "***"
            },
            "target": {
                "bucket": "result-data"
            },
            "type": "s3"
        }

        training_references = [
            {
                "training_definition_url": "https://ibm-watson-ml.mybluemix.net/v3/ml_assets/training_definitions/12345",
                "compute_configuration": {"name": "small"}
            },
            {
                "training_definition_url": "https://ibm-watson-ml.mybluemix.net/v3/ml_assets/training_definitions/67890",
            }
        ]

        return {
            self.NAME: "Hand-written Digit Recognition",
            self.DESCRIPTION: "Hand-written Digit Recognition training",
            self.AUTHOR_NAME: "John Smith",
            self.AUTHOR_EMAIL: "John.Smith@x.x",
            # self.OPTIMIZATION_METHOD: "random",
            # self.OPTIMIZATION_PARAMETERS: {},
            self.EVALUATION_METHOD: "multiclass",
            self.EVALUATION_METRICS: ["accuracy"],
            self.TRAINING_REFERENCES: training_references,
            self.TRAINING_DATA_REFERENCE: training_data_reference,
            self.TRAINING_RESULTS_REFERENCE: training_results_reference
        }


class TrainingConfigurationMetaNames:
    """
    Set of Meta Names for trainings.

    Available MetaNames:

    +-----------------------------------------------------------+------+----------+-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | MetaName                                                  | Type | Required | Default value                 | Example value                                                                                                                                                                                                                                        |
    +===========================================================+======+==========+===============================+======================================================================================================================================================================================================================================================+
    | TrainingConfigurationMetaNames.NAME                       | str  | Y        |                               | ``"Hand-written Digit Recognition"``                                                                                                                                                                                                                 |
    +-----------------------------------------------------------+------+----------+-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | TrainingConfigurationMetaNames.DESCRIPTION                | str  | N        |                               | ``"Hand-written Digit Recognition training"``                                                                                                                                                                                                        |
    +-----------------------------------------------------------+------+----------+-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | TrainingConfigurationMetaNames.AUTHOR_NAME                | str  | N        |                               | ``"John Smith"``                                                                                                                                                                                                                                     |
    +-----------------------------------------------------------+------+----------+-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | TrainingConfigurationMetaNames.AUTHOR_EMAIL               | str  | Y        |                               | ``"John.Smith@x.x"``                                                                                                                                                                                                                                 |
    +-----------------------------------------------------------+------+----------+-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | TrainingConfigurationMetaNames.FRAMEWORK_NAME             | str  | N        | <value from model definition> | ``"tensorflow"``                                                                                                                                                                                                                                     |
    +-----------------------------------------------------------+------+----------+-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | TrainingConfigurationMetaNames.FRAMEWORK_VERSION          | str  | N        | <value from model definition> | ``"1.2-py3"``                                                                                                                                                                                                                                        |
    +-----------------------------------------------------------+------+----------+-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | TrainingConfigurationMetaNames.TRAINING_DATA_REFERENCE    | json | Y        |                               | ``{"connection": {"auth_url": "https://identity.open.softlayer.com/v3", "user_name": "xxx", "password": "xxx", "region": "dallas", "domain_name": "xxx", "project_id": "xxx"}, "source": {"bucket": "train-data"}, "type": "bluemix_objectstore"}``  |
    +-----------------------------------------------------------+------+----------+-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | TrainingConfigurationMetaNames.TRAINING_RESULTS_REFERENCE | json | Y        |                               | ``{"connection": {"auth_url": "https://identity.open.softlayer.com/v3", "user_name": "xxx", "password": "xxx", "region": "dallas", "domain_name": "xxx", "project_id": "xxx"}, "target": {"bucket": "result-data"}, "type": "bluemix_objectstore"}`` |
    +-----------------------------------------------------------+------+----------+-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | TrainingConfigurationMetaNames.EXECUTION_COMMAND          | str  | N        | <value from model definition> | ``"python3 tensorflow_mnist_softmax.py --trainingIters 20"``                                                                                                                                                                                         |
    +-----------------------------------------------------------+------+----------+-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | TrainingConfigurationMetaNames.COMPUTE_CONFIGURATION    | str  | N        | ``"small"``                   | ``"small"``                                                                                                                                                                                                                                          |
    +-----------------------------------------------------------+------+----------+-------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

    """

    def __init__(self):
        self.NAME = "name"
        self.DESCRIPTION = "description"
        self.AUTHOR_NAME = "author_name"
        self.AUTHOR_EMAIL = "author_email"
        self.FRAMEWORK_NAME = "framework_name"
        self.FRAMEWORK_VERSION = "framework_version"
        # TODO needed when bug fixed
        #self.RUNTIME_NAME = "runtime_name"
        #self.RUNTIME_VERSION = "runtime_version"
        self.TRAINING_DATA_REFERENCE = "training_data"
        self.TRAINING_RESULTS_REFERENCE = "training_results"
        self.EXECUTION_COMMAND = "command"
        # TODO this name or another?
        self.COMPUTE_CONFIGURATION = "compute_configuration_name"

        self._NAME_REQUIRED = True
        self._DESCRIPTION_REQUIRED = False
        self._AUTHOR_NAME_REQUIRED = False
        self._AUTHOR_EMAIL_REQUIRED = True
        self._FRAMEWORK_NAME_REQUIRED = False
        self._FRAMEWORK_VERSION_REQUIRED = False
        # TODO needed when bug fixed
        # self._RUNTIME_NAME_REQUIRED = False
        # self._RUNTIME_VERSION_REQUIRED = False
        self._TRAINING_DATA_REFERENCE_REQUIRED = True
        self._TRAINING_RESULTS_REFERENCE_REQUIRED = True
        self._EXECUTION_COMMAND_REQUIRED = False
        self._COMPUTE_CONFIGURATION_REQUIRED = False

    def _validate(self, meta_props):
        WMLResource._validate_meta_prop(meta_props, self.NAME, str, self._NAME_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.DESCRIPTION, str, self._DESCRIPTION_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.AUTHOR_NAME, str, self._AUTHOR_NAME_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.AUTHOR_EMAIL, str, self._AUTHOR_EMAIL_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.FRAMEWORK_NAME, str, self._FRAMEWORK_NAME_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.FRAMEWORK_VERSION, str, self._FRAMEWORK_VERSION_REQUIRED)
        # WMLResource._validate_meta_prop(meta_props, self.RUNTIME_NAME, str, self._RUNTIME_NAME_REQUIRED)
        # WMLResource._validate_meta_prop(meta_props, self.RUNTIME_VERSION, str, self._RUNTIME_VERSION_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.TRAINING_DATA_REFERENCE, object, self._TRAINING_DATA_REFERENCE_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.TRAINING_RESULTS_REFERENCE, object, self._TRAINING_RESULTS_REFERENCE_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.EXECUTION_COMMAND, str, self._EXECUTION_COMMAND_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.COMPUTE_CONFIGURATION, str, self._COMPUTE_CONFIGURATION_REQUIRED)

    def get(self):
        """
        Get available experiment metanames.

        :return: available experiment metanames
        :rtype: array
        """
        return sorted(list(filter(lambda x: not x.startswith('_'), self.__dict__.keys())))

    def show(self):
        """
            Shows possible metanames, type and if it is required.
        """
        table = tabulate(
            [
                ["META_PROP NAME",                  "TYPE",     "REQUIRED",                                                 "DEFAULT VALUE"],
                ["NAME",                         "str",      "Y" if self._NAME_REQUIRED else "N",                        ""],
                ["DESCRIPTION",                  "str",      "Y" if self._DESCRIPTION_REQUIRED else "N",                 ""],
                ["AUTHOR_NAME",                  "str",      "Y" if self._AUTHOR_NAME_REQUIRED else "N",                 ""],
                ["AUTHOR_EMAIL",                 "str",      "Y" if self._AUTHOR_EMAIL_REQUIRED else "N",                ""],
                ["FRAMEWORK_NAME",               "str",      "Y" if self._FRAMEWORK_NAME_REQUIRED else "N",              "<value from model definition>"],
                ["FRAMEWORK_VERSION",            "str",      "Y" if self._FRAMEWORK_VERSION_REQUIRED else "N",           "<value from model definition>"],
                # TODO needed when bug fixed
                #[self.RUNTIME_NAME, "str", "Y" if self._RUNTIME_NAME_REQUIRED else "N", ""],
                #[self.RUNTIME_VERSION, "str", "Y" if self._RUNTIME_VERSION_REQUIRED else "N", ""],
                ["TRAINING_DATA_REFERENCE",      "json",     "Y" if self._TRAINING_DATA_REFERENCE_REQUIRED else "N",     ""],
                ["TRAINING_RESULTS_REFERENCE",   "json",     "Y" if self._TRAINING_RESULTS_REFERENCE_REQUIRED else "N",  ""],
                ["EXECUTION_COMMAND",            "str",      "Y" if self._EXECUTION_COMMAND_REQUIRED else "N",           "<value from model definition>"],
                ["COMPUTE_CONFIGURATION",      "str",      "Y" if self._COMPUTE_CONFIGURATION_REQUIRED else "N",     "small"]
            ]
        )
        print(table)

    def get_example_values(self):
        """
        Get example values for metanames.

        :return: example meta_props
        :rtype: json
        """
        training_data_reference = {
            "connection": {
                "endpoint_url": "https://s3-api.us-geo.objectstorage.softlayer.net",
                "access_key_id": "***",
                "secret_access_key": "***"
            },
            "source": {
                "bucket": "train-data"
            },
            "type": "s3"
        }

        training_results_reference = {
            "connection": {
                "endpoint_url": "https://s3-api.us-geo.objectstorage.softlayer.net",
                "access_key_id": "***",
                "secret_access_key": "***"
            },
            "target": {
                "bucket": "train-data"
            },
            "type": "s3"
        }

        return {
            self.NAME: "Hand-written Digit Recognition",
            self.DESCRIPTION: "Hand-written Digit Recognition training",
            self.AUTHOR_NAME: "John Smith",
            self.AUTHOR_EMAIL: "John.Smith@x.x",
            self.FRAMEWORK_NAME: "tensorflow",
            self.FRAMEWORK_VERSION: "1.2-py3",
            # TODO needed when bug fixed
            # self.RUNTIME_NAME: "python",
            # self.RUNTIME_VERSION: "3.5",
            self.TRAINING_DATA_REFERENCE: training_data_reference,
            self.TRAINING_RESULTS_REFERENCE: training_results_reference,
            self.EXECUTION_COMMAND: "python3 tensorflow_mnist_softmax.py --trainingIters 20",
            self.COMPUTE_CONFIGURATION: {"name": "small"}
        }


class ModelDefinitionMetaNames:
    """
    Set of Meta Names for model definitions.

    Available MetaNames:

    +---------------------------------------------+------+----------+--------------------------------------------------------------+
    | MetaName                                    | Type | Required | Example value                                                |
    +=============================================+======+==========+==============================================================+
    | ModelDefinitionMetaNames.NAME               | str  | Y        | ``"Hand-written Digit Recognition"``                         |
    +---------------------------------------------+------+----------+--------------------------------------------------------------+
    | ModelDefinitionMetaNames.DESCRIPTION        | str  | N        | ``"Hand-written Digit Recognition training"``                |
    +---------------------------------------------+------+----------+--------------------------------------------------------------+
    | ModelDefinitionMetaNames.AUTHOR_NAME        | str  | N        | ``"John Smith"``                                             |
    +---------------------------------------------+------+----------+--------------------------------------------------------------+
    | ModelDefinitionMetaNames.AUTHOR_EMAIL       | str  | Y        | ``"John.Smith@x.x"``                                         |
    +---------------------------------------------+------+----------+--------------------------------------------------------------+
    | ModelDefinitionMetaNames.FRAMEWORK_NAME     | str  | Y        | ``"tensorflow"``                                             |
    +---------------------------------------------+------+----------+--------------------------------------------------------------+
    | ModelDefinitionMetaNames.FRAMEWORK_VERSION  | str  | Y        | ``"1.2"``                                                    |
    +---------------------------------------------+------+----------+--------------------------------------------------------------+
    | ModelDefinitionMetaNames.RUNTIME_NAME       | str  | Y        | ``"python"``                                                 |
    +---------------------------------------------+------+----------+--------------------------------------------------------------+
    | ModelDefinitionMetaNames.RUNTIME_VERSION    | str  | Y        | ``"3.5"``                                                    |
    +---------------------------------------------+------+----------+--------------------------------------------------------------+
    | ModelDefinitionMetaNames.EXECUTION_COMMAND  | str  | Y        | ``"python3 tensorflow_mnist_softmax.py --trainingIters 20"`` |
    +---------------------------------------------+------+----------+--------------------------------------------------------------+
    """

    def __init__(self):
        self.NAME = "name"
        self.DESCRIPTION = "description"
        self.AUTHOR_NAME = "author_name"
        self.AUTHOR_EMAIL = "author_email"
        self.FRAMEWORK_NAME = "framework_name"
        self.FRAMEWORK_VERSION = "framework_version"
        self.RUNTIME_NAME = "runtime_name"
        self.RUNTIME_VERSION = "runtime_version"
        self.EXECUTION_COMMAND = "command"

        self._NAME_REQUIRED = True
        self._DESCRIPTION_REQUIRED = False
        self._AUTHOR_NAME_REQUIRED = False
        self._AUTHOR_EMAIL_REQUIRED = True
        self._FRAMEWORK_NAME_REQUIRED = True
        self._FRAMEWORK_VERSION_REQUIRED = True
        self._RUNTIME_NAME_REQUIRED = True
        self._RUNTIME_VERSION_REQUIRED = True
        self._EXECUTION_COMMAND_REQUIRED = True

    def _validate(self, meta_props):
        WMLResource._validate_meta_prop(meta_props, self.NAME, str, self._NAME_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.DESCRIPTION, str, self._DESCRIPTION_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.AUTHOR_NAME, str, self._AUTHOR_NAME_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.AUTHOR_EMAIL, str, self._AUTHOR_EMAIL_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.FRAMEWORK_NAME, str, self._FRAMEWORK_NAME_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.FRAMEWORK_VERSION, str, self._FRAMEWORK_VERSION_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.RUNTIME_NAME, str, self._RUNTIME_NAME_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.RUNTIME_VERSION, str, self._RUNTIME_VERSION_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.EXECUTION_COMMAND, str, self._EXECUTION_COMMAND_REQUIRED)

    def get(self):
        """
        Get available experiment metanames.

        :return: available experiment metanames
        :rtype: array
        """
        return sorted(list(filter(lambda x: not x.startswith('_'), self.__dict__.keys())))

    def show(self):
        """
            Shows possible metanames, type and if it is required.
        """
        table = tabulate(
            [
                ["META_PROP NAME",          "TYPE", "REQUIRED"],
                ["NAME",                 "str",  "Y" if self._NAME_REQUIRED else "N"],
                ["DESCRIPTION",          "str",  "Y" if self._DESCRIPTION_REQUIRED else "N"],
                ["AUTHOR_NAME",          "str",  "Y" if self._AUTHOR_NAME_REQUIRED else "N"],
                ["AUTHOR_EMAIL",         "str",  "Y" if self._AUTHOR_EMAIL_REQUIRED else "N"],
                ["FRAMEWORK_NAME",       "str",  "Y" if self._FRAMEWORK_NAME_REQUIRED else "N"],
                ["FRAMEWORK_VERSION",    "str",  "Y" if self._FRAMEWORK_VERSION_REQUIRED else "N"],
                ["RUNTIME_NAME",         "str",  "Y" if self._RUNTIME_NAME_REQUIRED else "N"],
                ["RUNTIME_VERSION",      "str",  "Y" if self._RUNTIME_VERSION_REQUIRED else "N"],
                ["EXECUTION_COMMAND",    "str",  "Y" if self._EXECUTION_COMMAND_REQUIRED else "N"]
            ]
        )
        print(table)

    def get_example_values(self):
        """
            Get example values for metanames.

            :return: example meta_props
            :rtype: json
        """
        return {
            self.NAME: "my_training_definition",
            self.DESCRIPTION: "my_description",
            self.AUTHOR_NAME: "John Smith",
            self.AUTHOR_EMAIL: "John.Smith@x.x",
            self.FRAMEWORK_NAME: "tensorflow",
            self.FRAMEWORK_VERSION: "1.2",
            self.RUNTIME_NAME: "python",
            self.RUNTIME_VERSION: "3.5",
            self.EXECUTION_COMMAND: "python3 tensorflow_mnist_softmax.py --trainingIters 20"
        }


class ModelMetaNames:
    """
    Set of Meta Names for models.

    Available MetaNames:

    +---------------------------------------------+------+----------+--------------------------------------------------------------+
    | MetaName                                    | Type | Required | Example value                                                |
    +=============================================+======+==========+==============================================================+
    | ModelDefinitionMetaNames.NAME               | str  | Y        | ``"my_model"``                                               |
    +---------------------------------------------+------+----------+--------------------------------------------------------------+
    | ModelDefinitionMetaNames.DESCRIPTION        | str  | N        | ``"my_description"``                                         |
    +---------------------------------------------+------+----------+--------------------------------------------------------------+
    | ModelDefinitionMetaNames.AUTHOR_NAME        | str  | N        | ``"John Smith"``                                             |
    +---------------------------------------------+------+----------+--------------------------------------------------------------+
    | ModelDefinitionMetaNames.AUTHOR_EMAIL       | str  | N        | ``"John.Smith@x.x"``                                         |
    +---------------------------------------------+------+----------+--------------------------------------------------------------+
    | ModelDefinitionMetaNames.FRAMEWORK_NAME     | str  | N        | ``"tensorflow"``                                             |
    +---------------------------------------------+------+----------+--------------------------------------------------------------+
    | ModelDefinitionMetaNames.FRAMEWORK_VERSION  | str  | N        | ``"1.2"``                                                    |
    +---------------------------------------------+------+----------+--------------------------------------------------------------+
    | ModelDefinitionMetaNames.RUNTIME_NAME       | str  | N        | ``"python"``                                                 |
    +---------------------------------------------+------+----------+--------------------------------------------------------------+
    | ModelDefinitionMetaNames.RUNTIME_VERSION    | str  | N        | ``"3.5"``                                                    |
    +---------------------------------------------+------+----------+--------------------------------------------------------------+
    """

    def __init__(self):
        self.NAME = "name"
        self.DESCRIPTION = MetaNames.DESCRIPTION
        self.AUTHOR_NAME = MetaNames.AUTHOR_NAME
        self.AUTHOR_EMAIL = MetaNames.AUTHOR_EMAIL
        self.FRAMEWORK_NAME = MetaNames.FRAMEWORK_NAME
        self.FRAMEWORK_VERSION = MetaNames.FRAMEWORK_VERSION
        self.RUNTIME_NAME = "runtime_name"
        self.RUNTIME_VERSION = "runtime_version"

        self._NAME_REQUIRED = True
        self._DESCRIPTION_REQUIRED = False
        self._AUTHOR_NAME_REQUIRED = False
        self._AUTHOR_EMAIL_REQUIRED = False
        self._FRAMEWORK_NAME_REQUIRED = False
        self._FRAMEWORK_VERSION_REQUIRED = False
        self._RUNTIME_NAME_REQUIRED = False
        self._RUNTIME_VERSION_REQUIRED = False


    def _validate(self, meta_props):
        WMLResource._validate_meta_prop(meta_props, self.NAME, str, self._NAME_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.DESCRIPTION, str, self._DESCRIPTION_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.AUTHOR_NAME, str, self._AUTHOR_NAME_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.AUTHOR_EMAIL, str, self._AUTHOR_EMAIL_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.FRAMEWORK_NAME, str, self._FRAMEWORK_NAME_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.FRAMEWORK_VERSION, str, self._FRAMEWORK_VERSION_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.RUNTIME_NAME, str, self._RUNTIME_NAME_REQUIRED)
        WMLResource._validate_meta_prop(meta_props, self.RUNTIME_VERSION, str, self._RUNTIME_VERSION_REQUIRED)

    def get(self):
        """
        Get available experiment metanames.

        :return: available experiment metanames
        :rtype: array
        """
        return sorted(list(filter(lambda x: not x.startswith('_'), self.__dict__.keys())))

    def show(self):
        """
            Shows possible metanames, type and if it is required.
        """
        table = tabulate(
            [
                ["META_PROP NAME",          "TYPE", "REQUIRED"],
                ["NAME",                 "str",  "Y" if self._NAME_REQUIRED else "N"],
                ["DESCRIPTION",          "str",  "Y" if self._DESCRIPTION_REQUIRED else "N"],
                ["AUTHOR_NAME",          "str",  "Y" if self._AUTHOR_NAME_REQUIRED else "N"],
                ["AUTHOR_EMAIL",         "str",  "Y" if self._AUTHOR_EMAIL_REQUIRED else "N"],
                ["FRAMEWORK_NAME",       "str",  "Y" if self._FRAMEWORK_NAME_REQUIRED else "N"],
                ["FRAMEWORK_VERSION",    "str",  "Y" if self._FRAMEWORK_VERSION_REQUIRED else "N"],
                ["RUNTIME_NAME",         "str",  "Y" if self._RUNTIME_NAME_REQUIRED else "N"],
                ["RUNTIME_VERSION",      "str",  "Y" if self._RUNTIME_VERSION_REQUIRED else "N"]
            ]
        )
        print(table)

    def get_example_values(self):
        """
            Get example values for metanames.

            :return: example meta_props
            :rtype: json
        """
        return {
            self.NAME: "my_model",
            self.DESCRIPTION: "my_description",
            self.AUTHOR_NAME: "John Smith",
            self.AUTHOR_EMAIL: "John.Smith@x.x",
            self.FRAMEWORK_NAME: "tensorflow",
            self.FRAMEWORK_VERSION: "1.2",
            self.RUNTIME_NAME: "python",
            self.RUNTIME_VERSION: "3.5"
        }