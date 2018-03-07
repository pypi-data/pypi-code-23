#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

"""
WinMLTools
This framework converts ML models into ONNX for use with Windows Machine Learning
"""
__version__ = "0.1.0.5072"
__author__ = "Microsoft Corporation"
__producer__ = "WinMLTools"

from .convert import convert_coreml
from .convert import convert_sklearn
from .convert import convert_xgboost
from .convert import convert_libsvm

from .utils import load_model
from .utils import save_text

# Overrides for onnxmltools
import onnxmltools
onnxmltools.__producer__ = __producer__
onnxmltools.__producer_version__ = __version__

