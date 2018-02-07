# -*- coding: utf-8 -*-
import os
import tempfile
import subprocess
import tensorflow as tf
from tensorflow.core.framework.types_pb2 import DataType
from modelhub.core.models import ModelVersion


def get_meta_graph_def(saved_model_def, tag_set)->tf.MetaGraphDef:
    set_of_tags = set(tag_set.split(','))
    for meta_graph_def in saved_model_def.meta_graphs:
        if set(meta_graph_def.meta_info_def.tags) == set_of_tags:
            return meta_graph_def


def optimize(model_version: ModelVersion, transform_graph_path, output_path=None):
    saved_model_def = model_version.saved_model_def
    for meta_graph_def in saved_model_def.meta_graphs:
        transformed_graph = transform_graph(meta_graph_def, transform_graph_path, model_version.local_path)
        meta_graph_def.graph_def.CopyFrom(transformed_graph)
    if output_path:
        with open(output_path, "wb") as f:
            f.write(saved_model_def.SerializeToString())
    else:
        return saved_model_def


def inspect_meta_graph_io(meta_graph_def):
    output_node_names = [
        output_node.name.split(":")[0]
        for signature_def in meta_graph_def.signature_def.values()
        for output_node in signature_def.outputs.values()
    ]
    input_nodes_name_type_shape = [
        (
            input_node.name.split(":")[0],
            DataType.Name(input_node.dtype)[3:].lower(),
            [dim.size for dim in input_node.tensor_shape.dim]
        )
        for signature_def in meta_graph_def.signature_def.values()
        for input_node in signature_def.inputs.values()
    ]
    return input_nodes_name_type_shape, output_node_names


def freeze_model(meta_graph_def, input_saved_model_dir):
    _, output_node_names = inspect_meta_graph_io(meta_graph_def)
    tags = list(meta_graph_def.meta_info_def.tags)
    from tensorflow.python.tools.freeze_graph import freeze_graph_with_def_protos
    frozen_graph_def = freeze_graph_with_def_protos(
        input_graph_def=meta_graph_def.graph_def,
        input_saver_def=None,
        input_checkpoint=None,
        # input_meta_graph_def=meta_graph_def,
        input_saved_model_dir=input_saved_model_dir,
        saved_model_tags=tags,
        output_node_names=",".join(output_node_names),
        restore_op_name=None,
        filename_tensor_name=None,
        output_graph=None,
        clear_devices=False,
        initializer_nodes=None
    )
    # meta_graph_def.graph_def.CopyFrom(frozen_graph_def)
    return frozen_graph_def


def transform_graph(meta_graph_def, transform_graph_path, input_saved_model_dir):
    with tempfile.NamedTemporaryFile() as f:
        frozen_graph_def = freeze_model(meta_graph_def, input_saved_model_dir)
        input_nodes_name_type_shape, output_node_names = inspect_meta_graph_io(meta_graph_def)

        f.write(frozen_graph_def.SerializeToString())
        f.flush()
        output_name = tempfile.mktemp()
        status = subprocess.run(" ".join([
            transform_graph_path,
            "--in_graph=" + f.name,
            "--out_graph=" + output_name,
            "--inputs='%s'" % ",".join(name for name, type, shape in input_nodes_name_type_shape),
            "--outputs='%s'" % ",".join(output_node_names),
            "--transforms='  %s'" % "\n  ".join(generate_transforms(input_nodes_name_type_shape))
        ]), shell=True)
    if status.returncode:
        raise ValueError("Error transform")

    with open(output_name, "rb") as f:
        new_graph = tf.GraphDef()
        new_graph.ParseFromString(f.read())
    os.unlink(output_name)
    return new_graph


def generate_transforms(input_nodes_name_type_shape):
    return [
        "add_default_attributes",
        # "strip_unused_nodes(type=float, shape="1,299,299,3")",
        generate_strip_unused_nodes(input_nodes_name_type_shape),
        "remove_nodes(op=Identity, op=CheckNumerics)",
        "fold_constants(ignore_errors=true)",
        "fold_batch_norms",
        "fold_old_batch_norms",
        "quantize_weights",
        "quantize_nodes",
        "strip_unused_nodes",
        "sort_by_execution_order",
    ]

    # return [
    #     generate_strip_unused_nodes(input_nodes_name_type_shape),
    #     "fold_constants(ignore_errors=true)",
    #     "fold_batch_norms",
    #     "fold_old_batch_norms",
    #     "quantize_weights",
    # ]


def generate_strip_unused_nodes(input_nodes_name_type_shape):
    args = ", ".join(
        'name={name}, type_for_name={type}, shape_for_name="{shape}"'.format(
            name=name,
            type=type,
            shape=",".join(str(dim) for dim in shape)
        )
        for name, type, shape in input_nodes_name_type_shape
    )
    return "strip_unused_nodes(%s)" % args
