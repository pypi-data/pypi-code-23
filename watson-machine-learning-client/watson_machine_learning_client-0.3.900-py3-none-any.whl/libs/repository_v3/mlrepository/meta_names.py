################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################


class MetaNames(object):
    """
    Holder for constants used by MetaProps.

    Description of keys:

    +--------------------------------+---------+---------+---------+--------+-------------------------------------------------+
    |Key name                        |User     |Used with|Used with|Optional|Description                                      |
    |                                |specified|pipeline |model    |        |                                                 |
    +================================+=========+=========+=========+========+=================================================+
    |MetaNames.CREATION_TIME         |No       |Yes      |Yes      |--      |time of creating artifact in repository service  |
    +--------------------------------+---------+---------+---------+--------+-------------------------------------------------+
    |MetaNames.LAST_UPDATED          |No       |Yes      |Yes      |--      |time of last update of this artifact             |
    |                                |         |         |         |        |in repository service                            |
    +--------------------------------+---------+---------+---------+--------+-------------------------------------------------+
    |MetaNames.TRAINING_DATA_REF     |Yes      |No       |Yes      |Yes     |reference to training data for model             |
    +--------------------------------+---------+---------+---------+--------+-------------------------------------------------+
    |MetaNames.LABEL_FIELD           |No       |No       |Yes      |--      |information about model what is the name         |
    |                                |         |         |         |        |of output column (labelCol)                      |
    +--------------------------------+---------+---------+---------+--------+-------------------------------------------------+
    |MetaNames.PARENT_VERSION        |No       |Yes      |Yes      |--      |href to previous version of artifact             |
    +--------------------------------+---------+---------+---------+--------+-------------------------------------------------+
    |MetaNames.VERSION               |No       |Yes      |Yes      |--      |id of version of artifact                        |
    +--------------------------------+---------+---------+---------+--------+-------------------------------------------------+
    |MetaNames.MODEL_METRICS         |--       |No       |Yes      |--      |modelMetrics                                     |
    +--------------------------------+---------+---------+---------+--------+-------------------------------------------------+
    |MetaNames.EVALUATION_METHOD     |--       |No       |Yes      |--      |evaluationMethod                                 |
    +--------------------------------+---------+---------+---------+--------+-------------------------------------------------+
    |MetaNames.EVALUATION_METRICS    |--       |No       |Yes      |--      |evaluationMetrics                                |
    +--------------------------------+---------+---------+---------+--------+-------------------------------------------------+
    |MetaNames.FRAMEWORK_NAME        |Yes      |Yes      |Yes      |--      |Framework type name, used with experiment        |
    |                                |         |         |         |        |and models                                       |
    +--------------------------------+---------+---------+---------+--------+-------------------------------------------------+
    |MetaNames.FRAMEWORK_VERSION     |Yes      |Yes      |Yes      |--      |Framework type version, used with experiments    |
    |                                |         |         |         |        |and models                                       |
    +--------------------------------+---------+---------+---------+--------+-------------------------------------------------+
    |MetaNames.DESCRIPTION           |Yes      |Yes      |Yes      |Yes     |description prepared by user                     |
    +--------------------------------+---------+---------+---------+--------+-------------------------------------------------+
    |MetaNames.MODEL_VERSION_URL     |No       |No       |Yes      |--      |url to version of this model in repository       |
    |                                |         |         |         |        |service, used only with models                   |
    +--------------------------------+---------+---------+---------+--------+-------------------------------------------------+
    |MetaNames.EXPERIMENT_VERSION_URL|No       |Yes      |No       |--      |url to version of this experiment in repository  |
    |                                |         |         |         |        |service, used only with experiment               |
    +--------------------------------+---------+---------+---------+--------+-------------------------------------------------+
    |MetaNames.AUTHOR_NAME           |Yes      |Yes      |Yes      |Yes     |name of author                                   |
    +--------------------------------+---------+---------+---------+--------+-------------------------------------------------+
    |MetaNames.AUTHOR_EMAIL          |Yes      |Yes      |Yes      |Yes     |email of author                                  |
    +--------------------------------+---------+---------+---------+--------+-------------------------------------------------+
    |MetaNames.EXPERIMENT_URL        |No       |Yes      |No       |--      |Url to this experiment in repository             |
    +--------------------------------+---------+---------+---------+--------+-------------------------------------------------+
    |MetaNames.MODEL_URL             |No       |No       |Yes      |--      |Url to this model in repository                  |
    +--------------------------------+---------+---------+---------+--------+-------------------------------------------------+

    """
    CREATION_TIME = "creationTime"
    LAST_UPDATED = "lastUpdated"
    INPUT_DATA_SCHEMA = "inputDataSchema"
    TRAINING_DATA_REFERENCE = "trainingDataReference"
    RUNTIME = "runtime"
    RUNTIMES = "runtimes"
    TRAINING_DATA_SCHEMA = "trainingDataSchema"
    LABEL_FIELD = "label_column"
    PARENT_VERSION = "parentVersion"
    VERSION = "version"
    MODEL_METRICS = "modelMetrics"
    EVALUATION_METHOD = "evaluationMethod"
    EVALUATION_METRICS = "evaluationMetrics"
    FRAMEWORK_NAME = "frameworkName"
    FRAMEWORK_VERSION = "frameworkVersion"
    FRAMEWORK_LIBRARIES = "frameworkLibraries"
    DESCRIPTION = "description"
    MODEL_VERSION_URL = "modelVersionUrl"
    TRAINING_DEFINITION_VERSION_URL = "trainingDefinitionVersionUrl"
    AUTHOR_NAME = "authorName"
    AUTHOR_EMAIL = "authorEmail"
    EXPERIMENT_URL = "experimentUrl"
    TRAINING_DEFINITION_URL = "trainingDefinitionUrl"
    MODEL_URL = "modelUrl"
    TRANSFORMED_LABEL_FIELD = "transformed_label"
    CONTENT_STATUS = "contentStatus"
    CONTENT_LOCATION = "contentLocation"
    HYPER_PARAMETERS = "hyperParameters"

    supported_frameworks_tar_gz = ["tensorflow","spss-modeler","pmml","caffe","caffe2",
                                   "pytorch","blueconnect","torch","mxnet","theano","darknet"]
    @staticmethod
    def is_supported_tar_framework(framework_name):
        if framework_name in MetaNames.supported_frameworks_tar_gz:
            return True
        else:
            return False

    @staticmethod
    def is_archive_framework(framework_name):
        if framework_name in ["spss-modeler","pmml","caffe","caffe2","pytorch","blueconnect","torch","mxnet","theano","darknet"]:
            return True
        else:
            return False

    class EXPERIMENTS(object):
        TAGS = "tags"
        SETTINGS = "settings"
        TRAINING_RESULTS_REFERENCE = "trainingResultsReference"
        TRAINING_REFERENCES = "trainingReferences"
        TRAINING_DATA_REFERENCE = "trainingDataReference"
        PATCH_INPUT = "experimentPatchInput"









