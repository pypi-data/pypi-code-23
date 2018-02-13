################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################


import logging
import re

from repository_v3.mlrepository import MetaNames, MetaProps, ModelArtifact
from repository_v3.mlrepository.scikit_model_artifact import ScikitModelArtifact
from repository_v3.mlrepository.tensorflow_model_artifact import TensorflowModelArtifact
from repository_v3.mlrepository.generic_archive_model_artifact import GenericArchiveModelArtifact
from repository_v3.mlrepositoryartifact import SparkPipelineModelLoader, SparkPipelineModelContentLoader,\
    IBMSparkPipelineModelContentLoader, MLPipelineModelContentLoader
from repository_v3.mlrepositoryartifact.content_loaders import ScikitPipelineModelContentLoader,TensorflowPipelineModelContentLoader
from repository_v3.mlrepositoryartifact.scikit_pipeline_model_loader import ScikitPipelineModelLoader
from repository_v3.mlrepositoryartifact.tensorflow_pipeline_model_loader import TensorflowPipelineModelLoader
from repository_v3.mlrepositoryartifact.generic_file_pipeline_model_loader import GenericFilePipelineModelLoader
from repository_v3.swagger_client.models import AuthorRepository
from repository_v3.util.generic_archive_file_check import GenericArchiveFrameworkCheck
import ast,json

from repository_v3.util.library_imports import LibraryChecker
from repository_v3.base_constants import *

lib_checker = LibraryChecker()

logger = logging.getLogger('ModelAdapter')


class ModelAdapter(object):
    """
    Adapter creating pipeline model artifact using output from service.
    """

    @staticmethod
    def __strip_output(output):
        return ast.literal_eval(json.dumps(output))

    def __init__(self, model_output, model_version_output, client):
        self.model_output = model_output
        self.model_version_output = model_version_output
        self.client = client
        self.model_type = model_output.entity['framework']
        self.model_entity = model_output.entity
        self.model_metadata = model_output.metadata

    def artifact(self):
        if re.match('mllib', self.model_type['name']) is not None:
            lib_checker.check_lib(PYSPARK)
            model_artifact_builder = type(
                "ModelArtifact",
                (SparkPipelineModelContentLoader, SparkPipelineModelLoader, ModelArtifact, object),
                {}
            )
        elif re.match('wml', self.model_type['name']) is not None:
            lib_checker.check_lib(PYSPARK)
            lib_checker.check_lib(MLPIPELINE)
            model_artifact_builder = type(
                "WMLModelArtifact",
                (MLPipelineModelContentLoader, SparkPipelineModelLoader, ModelArtifact, object),
                {}
            )
        elif re.match('scikit-learn', self.model_type['name']) is not None:
            lib_checker.check_lib(SCIKIT)
            model_artifact_builder = type(
                "ScikitModelArtifact",
                (ScikitPipelineModelContentLoader, ScikitPipelineModelLoader, ScikitModelArtifact, object),
                {}
            )
        elif re.match('tensorflow', self.model_type['name']) is not None:
            lib_checker.check_lib(TENSORFLOW)
            model_artifact_builder = type(
                "TensorflowModelArtifact",
                (TensorflowPipelineModelContentLoader, TensorflowPipelineModelLoader, TensorflowModelArtifact, object),
                {}
            )

        elif re.match('xgboost', self.model_type['name']) is not None:
            lib_checker.check_lib(SCIKIT)
            lib_checker.check_lib(XGBOOST)
            model_artifact_builder = type(
                "ScikitModelArtifact",
                (ScikitPipelineModelContentLoader, ScikitPipelineModelLoader, ScikitModelArtifact, object),
                {}
            )
        elif GenericArchiveFrameworkCheck.is_archive_framework(self.model_type['name']):
            model_artifact_builder = type(
                "GenericModelArchiveArtifact",
                (GenericFilePipelineModelLoader, GenericArchiveModelArtifact, object),
                {}
            )
        else:
            raise ValueError('Invalid model_type: {}'.format(self.model_type.get('name')))

        prop_map = {
            MetaNames.FRAMEWORK_VERSION: self.model_type.get('version'),
            MetaNames.FRAMEWORK_NAME: self.model_type.get('name')
        }

        if self.model_type.get('runtime') is not None:
            runtime = self.model_type.get('runtime')
            prop_map[MetaNames.RUNTIME] = runtime['name']  + "-" + runtime['version']

        if self.model_type.get('runtimes') is not None:
            prop_map[MetaNames.RUNTIMES] = self.model_type.get('runtimes')

        if 'libraries' in self.model_type:
            if self.model_type.get('libraries') is not None:
                prop_map[MetaNames.FRAMEWORK_LIBRARIES] = self.model_type.get('libraries')

        if self.model_metadata.created_at is not None:
            prop_map[MetaNames.CREATION_TIME] = self.model_output.metadata.created_at

        if self.model_output.metadata.modified_at is not None:
            prop_map[MetaNames.LAST_UPDATED] = self.model_output.metadata.modified_at

        # pipeline_version is not present for scikit model
        if self.model_entity.get('framework').get('name').startswith('mllib'):
            if self.model_entity.get('training_definition_url') is not None:
                training_def_ver_url = self.model_entity.get('training_definition_url')
                prop_map[MetaNames.TRAINING_DEFINITION_VERSION_URL] = training_def_ver_url

        if self.model_entity.get('label_column', None) is not None:
            prop_map[MetaNames.LABEL_FIELD] = self.model_entity.get('label_column')

        if self.model_entity.get('description', None) is not None:
            prop_map[MetaNames.DESCRIPTION] = self.model_entity.get('description')


        if self.model_entity.get('training_data_schema', None) is not None:
            prop_map[MetaNames.TRAINING_DATA_SCHEMA] = self.model_entity.get('training_data_schema')

        if self.model_entity.get('input_data_schema', None) is not None:
            prop_map[MetaNames.INPUT_DATA_SCHEMA] = self.model_entity.get('input_data_schema')

        if self.model_entity.get('transformed_label', None) is not None:
            prop_map[MetaNames.TRANSFORMED_LABEL_FIELD] = self.model_entity.get('transformed_label')



        #if self.model_entity.get('author', None) and isinstance(self.model_entity.get('author'), AuthorRepository):
        if self.model_entity.get('author', None) is not None:
            authorval = self.model_entity.get('author')
            if authorval.get('name', None ) is not None:
                prop_map[MetaNames.AUTHOR_NAME] = self.model_entity.get('author').get('name')
            if authorval.get('email', None ) is not None:
                prop_map[MetaNames.AUTHOR_EMAIL] = self.model_entity.get('author').get('email')

        if "training_data_reference" in self.model_entity and self.model_entity.get('training_data_reference', None) is not None:
                prop_map[MetaNames.TRAINING_DATA_REFERENCE] = self.model_entity.get('training_data_reference')
# TODO Fix Evaluation
        try:
            evaluation_data = self.model_entity.get('evaluation', None)
            if evaluation_data is not None:
                prop_map[MetaNames.EVALUATION_METHOD] = evaluation_data.get('method', None)
                if evaluation_data.get('metrics', None) is not None:
                    prop_map[MetaNames.EVALUATION_METRICS] = evaluation_data.get('metrics')
        #    evaluation_data = self.model_entity['evaluation']
        #    if evaluation_data is not None:t
        #        prop_map[MetaNames.EVALUATION_METHOD] = evaluation_data['method']
        #        if evaluation_data['metrics'] is not None:
        #           metrics = evaluation_data['metrics']
        #            prop_map[MetaNames.EVALUATION_METRICS] = metrics
        except KeyError:
            print("No Evlauation method given")

        #name = ''.join(map(lambda x: chr(ord(x)), self.model_output.entity['name']))
        name = self.model_entity.get('name')
        model_url = self.model_output.metadata.url
        model_id = model_url.split("/models/")[1].split("/")[0]


        model_artifact = model_artifact_builder(
            model_id,
            name,
            MetaProps(prop_map)
        )

        model_artifact.client = self.client

        if model_artifact.meta.prop(MetaNames.FRAMEWORK_NAME).startswith('mllib'):
            model_artifact._training_definition_version_url = model_artifact.meta.prop(MetaNames.TRAINING_DEFINITION_VERSION_URL)

        if model_artifact.meta.prop(MetaNames.FRAMEWORK_NAME).startswith('wml'):
            model_artifact._training_definition_version_url = model_artifact.meta.prop(MetaNames.TRAINING_DEFINITION_VERSION_URL)
        if self.model_version_output is not None:

            version_props = MetaProps({
                MetaNames.VERSION: self.model_version_output['guid'],
                MetaNames.MODEL_VERSION_URL: self.model_version_output['url']
            })
            # content_status, content_location = None, None
            if 'content_status' in self.model_version_output:
                if self.model_version_output['content_status'] is not None:
                    version_props.add(MetaNames.CONTENT_STATUS, self.model_version_output['content_status'])

            if 'content_location' in self.model_version_output:
                if self.model_version_output['content_location'] is not None:
                    version_props.add(MetaNames.CONTENT_LOCATION, self.model_version_output['content_location'])

            if 'hyper_parameters' in self.model_version_output:
                if self.model_version_output['hyper_parameters'] is not None:
                    version_props.add(MetaNames.HYPER_PARAMETERS, self.model_version_output['hyper_parameters'])

            model_artifact.meta.merge(version_props)

            model_artifact._content_href = self.model_version_output['content_url']
        else:
            model_artifact._content_href = None

        return model_artifact
