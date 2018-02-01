################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################


from .spark_pipeline_reader import SparkPipelineReader
from repository_v3.mlrepository import MetaNames, MetaProps, ModelArtifact
from repository_v3.util import SparkUtil,Json2ObjectMapper
from .version_helper import VersionHelper
from repository_v3.util.library_imports import LibraryChecker
from repository_v3.base_constants import *
from .spark_version import SparkVersion

lib_checker = LibraryChecker()
if lib_checker.installed_libs[PYSPARK]:
    from pyspark.ml.pipeline import Pipeline, PipelineModel
    from pyspark.sql import DataFrame

class SparkPipelineModelArtifact(ModelArtifact):
    """
    Class of model artifacts created with MLRepositoryCLient.

    :param pyspark.ml.PipelineModel ml_pipeline_model: Pipeline Model which will be wrapped
    :param DataFrame training_data: training_data compatible with Pipeline Model
    :param SparkPipelineArtifact pipeline_artifact: optional, pipeline artifact which Pipeline was used to generate Pipeline Model for this artifact

    :ivar pyspark.ml.PipelineModel ml_pipeline_model: Pipeline Model associated with this artifact
    :ivar DataFrame training_data: training_data compatible with Pipeline Model of this artifact
    """
    def __init__(self, ml_pipeline_model, training_data, uid=None, name=None, pipeline_artifact=None, meta_props=MetaProps({})):
        super(SparkPipelineModelArtifact, self).__init__(uid, name, meta_props)

        type_identified = False
        lib_checker.check_lib(PYSPARK)
        if issubclass(type(ml_pipeline_model), PipelineModel):
            if pipeline_artifact is not None:
                type_identified = True
            else:
                raise ValueError('Invalid input, pipeline_artifact can not be None for spark models.')

        if not type_identified and lib_checker.installed_libs[MLPIPELINE]:
            from mlpipelinepy.mlpipeline import MLPipelineModel
            if issubclass(type(ml_pipeline_model), MLPipelineModel):
                type_identified = True

        if not type_identified:
            raise ValueError('Invalid type for ml_pipeline: {}'.format(ml_pipeline_model.__class__.__name__))

        if not isinstance(training_data, DataFrame):
            raise ValueError('Invalid type for training_data: {}'.format(training_data.__class__.__name__))

        self.ml_pipeline_model = ml_pipeline_model
        self.training_data = training_data
        self._pipeline_artifact = pipeline_artifact

        if self._pipeline_artifact is not None:
            self.ml_pipeline = self._pipeline_artifact.pipeline_instance()
        else:
            try:
                from mlpipelinepy.mlpipeline import MLPipelineModel
                if issubclass(type(ml_pipeline_model), MLPipelineModel):
                    self.ml_pipeline = ml_pipeline_model.parent
            except:
                raise ValueError('Invalid type for ml_pipeline: {}'.format(ml_pipeline_model.__class__.__name__))


        if meta_props.prop(MetaNames.RUNTIMES) is None and meta_props.prop(MetaNames.RUNTIME) is None:
            ver = SparkVersion.significant()
            runtimes = '[{"name":"spark","version": "'+ ver + '"}]'
            self.meta.merge(
                MetaProps({MetaNames.RUNTIMES: runtimes})
            )


        # # TODO : Check and fix do we need to the merge training data ref
        self.meta.merge(
            MetaProps({
                MetaNames.FRAMEWORK_VERSION: VersionHelper.getFrameworkVersion(ml_pipeline_model),
                MetaNames.FRAMEWORK_NAME: VersionHelper.model_type(ml_pipeline_model),
                MetaNames.TRAINING_DATA_SCHEMA: Json2ObjectMapper.to_dict(self.training_data.schema.json()),
                MetaNames.LABEL_FIELD: SparkUtil.get_label_col(ml_pipeline_model) if meta_props.prop(MetaNames.LABEL_FIELD) is None else meta_props.prop(MetaNames.LABEL_FIELD)
            })
        )
        try:
            next(field for field in self.meta.prop(MetaNames.TRAINING_DATA_SCHEMA)['fields'] if field['name'] == self.meta.prop(MetaNames.LABEL_FIELD))
        except StopIteration:
            raise ValueError("Label \"{}\" cannot be found in training data schema.".format(self.meta.prop(MetaNames.LABEL_FIELD)))


    def pipeline_artifact(self):
        """
        Returns Pipeline artifact associated with this model artifact.

        If pipeline artifact was provided by user during creation - it will be returned. Otherwise will be created new pipeline artifact and returned.

        :return: Pipeline artifact associated with this Model artifact
        :rtype: SparkPipelineArtifact
        """
        if self._pipeline_artifact is None:

            from .ml_repository_artifact import MLRepositoryArtifact
            self._pipeline_artifact = MLRepositoryArtifact(ml_artifact=self.ml_pipeline, name=self.name, meta_props=self.meta)

        return self._pipeline_artifact

    def reader(self):
        """
        Returns reader used for getting pipeline model content.

        :return: reader for pyspark.ml.PipelineModel
        :rtype: SparkPipelineReader
        """
        try:
            return self._reader
        except:
            self._reader = SparkPipelineReader(self.ml_pipeline_model, 'model')
            return self._reader

    def _copy(self, uid=None, pipeline_artifact=None, meta_props=None):
        if uid is None:
            uid = self.uid

        if pipeline_artifact is None:
            pipeline_artifact = self.pipeline_artifact()

        if meta_props is None:
            meta_props = self.meta

        return SparkPipelineModelArtifact(
            self.ml_pipeline_model,
            training_data=self.training_data,
            uid=uid,
            name=self.name,
            pipeline_artifact=pipeline_artifact,
            meta_props=meta_props
        )
