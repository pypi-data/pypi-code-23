from repository_v3.mlrepository import MetaNames
from repository_v3.mlrepository import MetaProps
from repository_v3.mlrepository import ModelArtifact
from repository_v3.mlrepositoryartifact.tensorflow_pipeline_reader import TensorflowPipelineReader
from repository_v3.mlrepositoryartifact.generic_file_reader import GenericFileReader
from repository_v3.mlrepositoryartifact.version_helper import TensorflowVersionHelper
from repository_v3.util.library_imports import LibraryChecker
from repository_v3.base_constants import *
from .python_version import PythonVersion
from repository_v3.util.unique_id_gen import uid_generate
from repository_v3.util.exceptions import UnmatchedKerasVersion


class GenericArchivePipelineModelArtifact(ModelArtifact):
    """
    Class of  PMML,SPSS-MODELER,CAFFE,CAFFE2,PYTORCH,TORCH,MXNET,THEANO,BLUECONNECT and MXNET model artifacts created
    with MLRepositoryCLient.

    """
    def __init__(self,
                 generic_artifact,
                 uid=None,
                 name=None,
                 meta_props=MetaProps({}),):

        super(GenericArchivePipelineModelArtifact, self).__init__(uid, name, meta_props)

        self.ml_pipeline_model = generic_artifact
        self.ml_pipeline = None     # no pipeline or parent reference

    def pipeline_artifact(self):
        """
        Returns None. Pipeline is not implemented for archive model.
        """
        pass

    def reader(self):
        """
        Returns reader used for getting archive model content.

        :return: reader for TensorflowPipelineModelArtifact.pipeline.Pipeline
        :rtype: TensorflowPipelineReader
        """
        try:
            return self._reader
        except:
            self._reader = GenericFileReader(self.ml_pipeline_model)
            return self._reader

    def _copy(self, uid=None, meta_props=None):
        if uid is None:
            uid = self.uid

        if meta_props is None:
            meta_props = self.meta

        return GenericArchivePipelineModelArtifact(
            self.ml_pipeline_model,
            uid=uid,
            name=self.name,
            meta_props=meta_props
        )

