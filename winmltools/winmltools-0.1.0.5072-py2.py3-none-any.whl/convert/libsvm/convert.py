#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from ...proto import onnx_proto
from ..common import get_converter
from ..common import ModelBuilder
from ..common import model_util
from .SVMConvertContext import SVMConvertContext as ConvertContext

import sklearn.pipeline as pipeline

# These are not referenced directly but are imported
# to initialize the registration call
from .SVMConverter import AnyLibSvmConverter


def convert(model, name=None, input_features=None):
    if isinstance(model, str):
        # model is a path name
        model = _load_model(model)

    inputs = [model_util.make_tensor_value_info('Input', onnx_proto.TensorProto.FLOAT)]
    if input_features:
        inputs = []
        try:
            for input_name, input_type, input_shape in input_features:
                if not isinstance(input_shape, list):
                    input_shape = [1, input_shape]
                elem_type = model_util.tensorproto_typemap[input_type]
                inputs.append(model_util.make_tensor_value_info(input_name,
                                                                elem_type, input_shape))
            if len(input_features) > 1:
                nodes.append(_create_feature_vectorizer_node(context, inputs))
                inputs = nodes[-1].outputs
        except:
            raise ValueError('Invalid input_features argument.')
    
    converter = get_converter(type(model))
    onnx_nodes = []

    outputs = None
    converter.validate(model)

    context = ConvertContext()
    nodes = converter.convert(context, model, inputs)
    mb = ModelBuilder(name)
    for node in nodes:
        mb.add_nodes([node.onnx_node])
        mb.add_initializers(node.initializers)
        mb.add_values(node.values)    
    mb.add_inputs(inputs)
    mb.add_outputs(nodes[-1].outputs)
    return mb.make_model()


def _load_model(model_path):
    try:
        import svmutil
    except ImportError:
        raise ImportError("svmutil is required to load the model trained with libsvm.")
    return svmutil.load_model(model_path)
