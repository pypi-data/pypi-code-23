# -*- coding: utf-8 -*-
from __future__ import print_function
import os
from .base import BaseCommand, argument, option, types, register  # noqa
from modelhub.core.models import Model, ModelVersion
try:
    from tensorflow.core.framework import types_pb2
except:
    from tensorflow_protos.core.framework import types_pb2


@register("info")
class Command(BaseCommand):

    arguments = [
        argument("model_path_or_name"),
    ]

    def run(self, model_path_or_name):
        """
        Get info of a model
        """

        if self._is_model_path(model_path_or_name):
            self.local_model_info(model_path_or_name)
        else:
            model_name, version = Model.split_name_version(model_path_or_name)
            model = Model.get(name=model_name)
            if version is None:
                self.remote_list_version(model)
            else:
                self.remote_version_info(model.get_version(version))

    def _is_model_path(self, model_path_or_name):

        if "/" in model_path_or_name:
            return True
        if self._validate_path(model_path_or_name):
            return True

        return False

    def _validate_path(self, local_path):
        return os.path.exists(local_path)

    def local_model_info(self, model_path):
        # from tensorflow.contrib.saved_model.python.saved_model import reader
        # from tensorflow.python.tools.saved_model_cli import _show_all
        # saved_model = reader.read_saved_model(model_path)
        try:
            self._show_all(ModelVersion._load_saved_model(model_path))
        except OSError as e:
            print(e)
            print("Hint: perhaps forget version? Try add version_number")

    def remote_list_version(self, model):
        self._print_model_info(model)
        print("Versions:")
        for version in (model.versions):
            print("""id:\t{version.seq}
is_saved_model:\t{version.is_saved_model}
local:\t{is_local}
user:\t{version.submit_username}<{version.submit_email}>
date:\t{version_datetime}
comment:\t{version.comment}
require GPU:\t{version.require_gpu}
size:\t{version.compressed_size:,}
            """.format(
                model=model.manifest,
                version=version.manifest,
                version_datetime=version.manifest.submit_datetime.ToDatetime(),
                is_local=version.local_exists and version.local_path),
            )

    def _print_model_info(self, model):
        print("""name:\t{model.name}
desc:\t{model.description}
owner:\t{model.owner_name}<{model.owner_email}>
            """.format(model=model.manifest))

    def remote_version_info(self, version):
        self._print_model_info(version.model)
        print(version.manifest)

    def _show_all(self, saved_model):
        """Prints tag-set, SignatureDef and Inputs/Outputs information in SavedModel.

        Prints all tag-set, SignatureDef and Inputs/Outputs information stored in
        SavedModel directory.

        Args:
          saved_model: Directory containing the SavedModel to inspect.
        """
        tag_sets = self._get_saved_model_tag_sets(saved_model)
        for tag_set in sorted(tag_sets):
            tag_set = ', '.join(tag_set)
            print('\nMetaGraphDef with tag-set: \'' + tag_set +
                  '\' contains the following SignatureDefs:')

            signature_def_map = self._get_signature_def_map(saved_model, tag_set)
            for signature_def_key in sorted(signature_def_map.keys()):
                print('\nsignature_def[\'' + signature_def_key + '\']:')
                self._show_inputs_outputs(saved_model, tag_set, signature_def_key)

    def _get_saved_model_tag_sets(self, saved_model):
        """Retrieves all the tag-sets available in the SavedModel.

        Args:
          saved_model: Directory containing the SavedModel.

        Returns:
          String representation of all tag-sets in the SavedModel.
        """
        all_tags = []
        for meta_graph_def in saved_model.meta_graphs:
            all_tags.append(list(meta_graph_def.meta_info_def.tags))
        return all_tags

    def _get_signature_def_map(self, saved_model, tag_set):
        """Gets SignatureDef map from a MetaGraphDef in a SavedModel.

        Returns the SignatureDef map for the given tag-set in the SavedModel
        directory.

        Args:
          saved_model: Directory containing the SavedModel to inspect or execute.
          tag_set: Group of tag(s) of the MetaGraphDef with the SignatureDef map, in
              string format, separated by ','. For tag-set contains multiple tags, all
              tags must be passed in.

        Returns:
          A SignatureDef map that maps from string keys to SignatureDefs.
        """
        meta_graph = self._get_meta_graph_def(saved_model, tag_set)
        return meta_graph.signature_def

    def _get_meta_graph_def(self, saved_model, tag_set):
        """Gets MetaGraphDef from SavedModel.

        Returns the MetaGraphDef for the given tag-set and SavedModel directory.

        Args:
          saved_model: Directory containing the SavedModel to inspect or execute.
          tag_set: Group of tag(s) of the MetaGraphDef to load, in string format,
              separated by ','. For tag-set contains multiple tags, all tags must be
              passed in.

        Raises:
          RuntimeError: An error when the given tag-set does not exist in the
              SavedModel.

        Returns:
          A MetaGraphDef corresponding to the tag-set.
        """
        set_of_tags = set(tag_set.split(','))
        for meta_graph_def in saved_model.meta_graphs:
            if set(meta_graph_def.meta_info_def.tags) == set_of_tags:
                return meta_graph_def

        raise RuntimeError('MetaGraphDef associated with tag-set ' + tag_set +
                           ' could not be found in SavedModel')

    def _show_inputs_outputs(self, saved_model, tag_set, signature_def_key):
        """Prints input and output TensorInfos.

        Prints the details of input and output TensorInfos for the SignatureDef mapped
        by the given signature_def_key.

        Args:
          saved_model: Directory containing the SavedModel to inspect.
          tag_set: Group of tag(s) of the MetaGraphDef, in string format, separated by
              ','. For tag-set contains multiple tags, all tags must be passed in.
          signature_def_key: A SignatureDef key string.
        """
        meta_graph_def = self._get_meta_graph_def(saved_model, tag_set)
        inputs_tensor_info = self._get_inputs_tensor_info_from_meta_graph_def(
            meta_graph_def, signature_def_key)
        outputs_tensor_info = self._get_outputs_tensor_info_from_meta_graph_def(
            meta_graph_def, signature_def_key)

        print('The given SavedModel SignatureDef contains the following input(s):')
        for input_key, input_tensor in sorted(inputs_tensor_info.items()):
            print('inputs[\'%s\'] tensor_info:' % input_key)
            self._print_tensor_info(input_tensor)

        print('The given SavedModel SignatureDef contains the following output(s):')
        for output_key, output_tensor in sorted(outputs_tensor_info.items()):
            print('outputs[\'%s\'] tensor_info:' % output_key)
            self._print_tensor_info(output_tensor)

        print('Method name is: %s' %
              meta_graph_def.signature_def[signature_def_key].method_name)

    def _get_inputs_tensor_info_from_meta_graph_def(self, meta_graph_def,
                                                    signature_def_key):
        """Gets TensorInfo for all inputs of the SignatureDef.

        Returns a dictionary that maps each input key to its TensorInfo for the given
        signature_def_key in the meta_graph_def

        Args:
          meta_graph_def: MetaGraphDef protocol buffer with the SignatureDef map to
              look up SignatureDef key.
          signature_def_key: A SignatureDef key string.

        Returns:
          A dictionary that maps input tensor keys to TensorInfos.
        """
        return self._get_signature_def_by_key(meta_graph_def, signature_def_key).inputs

    def _get_outputs_tensor_info_from_meta_graph_def(self, meta_graph_def,
                                                     signature_def_key):
        """Gets TensorInfos for all outputs of the SignatureDef.

        Returns a dictionary that maps each output key to its TensorInfo for the given
        signature_def_key in the meta_graph_def.

        Args:
          meta_graph_def: MetaGraphDef protocol buffer with the SignatureDefmap to
          look up signature_def_key.
          signature_def_key: A SignatureDef key string.

        Returns:
          A dictionary that maps output tensor keys to TensorInfos.
        """
        return self._get_signature_def_by_key(meta_graph_def, signature_def_key).outputs

    def _print_tensor_info(self, tensor_info):
        """Prints details of the given tensor_info.

        Args:
          tensor_info: TensorInfo object to be printed.
        """
        print('    dtype: ' + types_pb2.DataType.keys()[tensor_info.dtype])
        # Display shape as tuple.
        if tensor_info.tensor_shape.unknown_rank:
            shape = 'unknown_rank'
        else:
            dims = [str(dim.size) for dim in tensor_info.tensor_shape.dim]
            shape = ', '.join(dims)
            shape = '(' + shape + ')'
        print('    shape: ' + shape)
        print('    name: ' + tensor_info.name)

    def _get_signature_def_by_key(self, meta_graph_def, signature_def_key):
      """Utility function to get a SignatureDef protocol buffer by its key.

      Args:
        meta_graph_def: MetaGraphDef protocol buffer with the SignatureDefMap to
          look up.
        signature_def_key: Key of the SignatureDef protocol buffer to find in the
          SignatureDefMap.

      Returns:
        A SignatureDef protocol buffer corresponding to the supplied key, if it
        exists.

      Raises:
        ValueError: If no entry corresponding to the supplied key is found in the
        SignatureDefMap of the MetaGraphDef.
      """
      if signature_def_key not in meta_graph_def.signature_def:
        raise ValueError("No SignatureDef with key '%s' found in MetaGraphDef." %
                         signature_def_key)
      return meta_graph_def.signature_def[signature_def_key]
