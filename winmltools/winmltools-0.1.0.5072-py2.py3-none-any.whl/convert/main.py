#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from .common import utils
from uuid import uuid4

def convert_sklearn(model, name=None, input_features=None):
    if not utils.sklearn_installed():
        raise RuntimeError('scikit-learn is not installed. Please install sci-kit learn to use this feature.')

    # import from onnxmltools
    from onnxmltools.convert.sklearn.convert import convert as _convert_sklearn

    # import from local sklearn to allow for overrides
    from . import sklearn

    return _convert_sklearn(model, name, input_features)


def convert_coreml(model, name=None):
    if not utils.coreml_installed():
        raise RuntimeError('coremltools is not installed. Please install coremltools to use this feature.')

    # import from onnxmltools
    from onnxmltools.convert.coreml.convert import convert as _convert_coreml

    # import from local coreml to allow for overrides
    from . import coreml

    return _convert_coreml(model, name)


def convert_libsvm(model, name=None, input_features=None):
    if not utils.libsvm_installed():
        raise RuntimeError('libsvm is not installed. Please install libsvm to use this feature.')
    from .libsvm.convert import convert
    return convert(model, name=name, input_features=input_features)


def convert_xgboost(model, name=None, input_features=None):
    if not utils.xgboost_installed():
        raise RuntimeError('xgboost not installed or not recent enough. Please install xgboost from github to use this feature.')

    from .xgboost.convert import convert
    return convert(model, name=name, input_features=input_features)
