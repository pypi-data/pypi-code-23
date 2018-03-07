# Copyright (c) 2017, Microsoft. All rights reserved.
#
# See LICENSE.txt.
"""
Main entry point to WinMLTools.
This framework converts any machine learned model into Lotus language
which is a common language to describe any machine learned model.
"""
__version__ = "0.1.0.5069"
__author__ = "Microsoft"
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

