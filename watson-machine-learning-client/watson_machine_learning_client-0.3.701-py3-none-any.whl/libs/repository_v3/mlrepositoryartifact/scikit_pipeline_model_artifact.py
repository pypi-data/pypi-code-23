################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################


from repository_v3.mlrepository import MetaNames
from repository_v3.mlrepository import MetaProps
from repository_v3.mlrepository import ModelArtifact
from repository_v3.util.library_imports import LibraryChecker
from repository_v3.base_constants import *
from .python_version import PythonVersion
import numpy as np

lib_checker = LibraryChecker()

if lib_checker.installed_libs[SCIKIT]:
    from repository_v3.mlrepositoryartifact.scikit_pipeline_reader import ScikitPipelineReader
    from repository_v3.mlrepositoryartifact.xgboost_model_reader import XGBoostModelReader
    from sklearn.base import BaseEstimator
    from repository_v3.mlrepositoryartifact.version_helper import ScikitVersionHelper, XGBoostVersionHelper

if lib_checker.installed_libs[XGBOOST]:
    from repository_v3.mlrepositoryartifact.version_helper import ScikitVersionHelper
    import xgboost as xgb


class ScikitPipelineModelArtifact(ModelArtifact):
    """
    Class of model artifacts created with MLRepositoryCLient.

    :param sklearn.pipeline.Pipeline scikit_pipeline_model: Pipeline Model which will be wrapped
    """
    def __init__(self, scikit_pipeline_model, training_features=None, training_target=None, feature_names=None,
                 label_column_names=None, uid=None, name=None, meta_props=MetaProps({})):
        lib_checker.check_lib(SCIKIT)
        super(ScikitPipelineModelArtifact, self).__init__(uid, name, meta_props)

        is_scikit, is_xgboost = False, False

        if issubclass(type(scikit_pipeline_model), BaseEstimator):
            is_scikit = True

        if not is_scikit and lib_checker.installed_libs[XGBOOST]:
            if isinstance(scikit_pipeline_model, xgb.Booster):
                is_xgboost = True

        if not (is_scikit or is_xgboost):
            raise ValueError('Invalid type for scikit ml_pipeline_model: {}'.
                             format(scikit_pipeline_model.__class__.__name__))

        self.ml_pipeline_model = scikit_pipeline_model
        self.ml_pipeline = None     # no pipeline or parent reference


        if meta_props.prop(MetaNames.RUNTIMES) is None and meta_props.prop(MetaNames.RUNTIME) is None:
            ver = PythonVersion.significant()
            runtimes = '[{"name":"python","version": "'+ ver + '"}]'
            self.meta.merge(
                MetaProps({MetaNames.RUNTIMES: runtimes})
            )
            
        if is_xgboost:
            self.meta.merge(
                MetaProps({
                    MetaNames.FRAMEWORK_NAME: XGBoostVersionHelper.model_type(scikit_pipeline_model),
                    MetaNames.FRAMEWORK_VERSION: XGBoostVersionHelper.model_version(scikit_pipeline_model)
                })
            )

            self._reader = XGBoostModelReader(self.ml_pipeline_model)
        else:
            self.meta.merge(
                MetaProps({
                    MetaNames.FRAMEWORK_NAME: ScikitVersionHelper.model_type(scikit_pipeline_model),
                    MetaNames.FRAMEWORK_VERSION: ScikitVersionHelper.model_version(scikit_pipeline_model)
                })
            )
            if(training_features is not None):
                if(training_target is None):
                    raise ValueError("Training target column has not been provided for the training data set")
                self.meta.merge(self._get_schema(training_features, training_target, feature_names, label_column_names))

            self._reader = ScikitPipelineReader(self.ml_pipeline_model)


    def _get_schema(self, training_features, training_target, feature_names, label_column_names):
        training_props = {
            "features": {"type": type(training_features).__name__, "fields": []},
            "labels": {"type": type(training_target).__name__, "fields": []}
        }

        lib_checker.check_lib(PANDAS)
        import pandas as pd

        # Check feature types, currently supporting pandas df, numpy.ndarray and python lists
        if(isinstance(training_features, pd.DataFrame)):
            for feature in training_features.dtypes.iteritems():
                training_props["features"]["fields"].append({"name": feature[0], "type": str(feature[1])})
        elif(isinstance(training_features, np.ndarray)):
            dims = training_features.shape
            if len(dims) == 1:
                if feature_names is None:
                    feature_names = 'f1'
                training_props["features"]["fields"].append({"name": feature_names, "type": type(training_features[0]).__name__})
            else:
                if feature_names is None:
                    feature_names = ['f' + str(i) for i in range(dims[1])]
                elif isinstance(feature_names, np.ndarray):
                    feature_names = feature_names.tolist()
                for i in range(dims[1]):
                    training_props["features"]["fields"].append({
                        "name": feature_names[i], "type": type(training_features[0][i].item()).__name__
                    })

        elif(isinstance(training_features, list)):
            if not isinstance(training_features[0], list):
                if feature_names is None:
                    feature_names = 'f1'
                training_props["features"]["fields"].append({"name": feature_names, "type": type(training_features[0]).__name__})
            else:
                if feature_names is None:
                    feature_names = ['f' + str(i) for i in range(len(training_features[0]))]
                elif isinstance(feature_names, np.ndarray):
                    feature_names = feature_names.tolist()
                for i in range(len(training_features[0])):
                    training_props["features"]["fields"].append({
                        "name": feature_names[i], "type": type(training_features[0][i]).__name__
                    })
        else:
            raise ValueError("Unsupported training data type %s provided" % (type(training_features).__name__))

        # Check target or label data types
        if(isinstance(training_target, pd.DataFrame)):
            for feature in training_target.dtypes.iteritems():
                training_props["labels"]["fields"].append({"name": feature[0], "type": str(feature[1])})
        elif(isinstance(training_target, pd.Series)):
            training_props["labels"]["fields"].append({"name": training_target.name, "type": str(training_target.dtype)})
        elif(isinstance(training_target, np.ndarray)):
            dims = training_target.shape
            if len(dims) == 1:
                if label_column_names is None:
                    label_column_names = 'l1'
                elif isinstance(label_column_names, list) or isinstance(label_column_names, np.ndarray):
                    label_column_names = label_column_names[0]
                training_props["labels"]["fields"].append({"name": label_column_names, "type": type(training_target[0].item()).__name__})
            else:
                if label_column_names is None:
                    label_column_names = ['l' + str(i) for i in range(dims[1])]
                elif isinstance(label_column_names, np.ndarray):
                    label_column_names = label_column_names.tolist()
                for i in range(dims[1]):
                    training_props["labels"]["fields"].append({
                        "name": label_column_names[i], "type": type(training_target[0][i].item()).__name__
                    })
        elif(isinstance(training_target, list)):
            if not isinstance(training_target[0], list):
                if label_column_names is None:
                    label_column_names = 'l1'
                elif isinstance(label_column_names, list) or isinstance(label_column_names, np.ndarray):
                    label_column_names = label_column_names[0]
                training_props["labels"]["fields"].append({
                    "name": label_column_names, "type": type(training_target[0]).__name__
                })
            else:
                if label_column_names is None:
                    label_column_names = ['l' + str(i) for i in range(len(training_target[0]))]
                elif isinstance(label_column_names, np.ndarray):
                    label_column_names = label_column_names.tolist()
                for i in range(len(training_features[0])):
                    training_props["labels"]["fields"].append({
                        "name": label_column_names[i], "type": type(training_target[0][i]).__name__
                    })
        else:
            raise ValueError("Unsupported label data type %s provided" % (type(training_target)))
        return MetaProps({
            MetaNames.TRAINING_DATA_SCHEMA: training_props,
            MetaNames.LABEL_FIELD: training_props["labels"]["fields"][0]["name"]
        })

    def pipeline_artifact(self):
        """
        Returns None. Pipeline is not implemented for scikit model.
        """
        pass

    def reader(self):
        """
        Returns reader used for getting pipeline model content.

        :return: reader for sklearn.pipeline.Pipeline
        :rtype: ScikitPipelineReader
        """

        return self._reader

    def _copy(self, uid=None, meta_props=None):
        if uid is None:
            uid = self.uid

        if meta_props is None:
            meta_props = self.meta

        return ScikitPipelineModelArtifact(
            self.ml_pipeline_model,
            uid=uid,
            name=self.name,
            meta_props=meta_props
        )
