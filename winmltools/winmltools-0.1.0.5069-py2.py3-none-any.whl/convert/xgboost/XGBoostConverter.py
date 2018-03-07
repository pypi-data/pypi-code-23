#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from ...proto import onnx_proto
from ..common import register_converter
from ..common import NodeBuilder
from ..common import utils
from ..common import model_util
from ..sklearn import add_zipmap
import ctypes
import numbers
import numpy
import json
from xgboost import XGBRegressor, XGBClassifier
from xgboost.core import _LIB, _check_call, from_cstr_to_pystr


class XGBConverter:
    
    @staticmethod
    def get_xgb_params(xgb_node):
        """
        Retrieves parameters of a model.
        """
        if hasattr(xgb_node, 'kwargs'):
            # XGBoost >= 0.7
            params = xgb_node.get_xgb_params()
        else:
            # XGBoost < 0.7
            params = xgb_node.__dict__
        return params        
    
    @staticmethod
    def validate(xgb_node):
        params = XGBConverter.get_xgb_params(xgb_node)
        try:
            if not "objective" in params:
                raise AttributeError('ojective')
        except AttributeError as e:
            raise RuntimeError('Missing attribute in XGBoost model ' + str(e))

    @staticmethod
    def common_members(xgb_node, inputs):
        params = XGBConverter.get_xgb_params(xgb_node)
        objective = params["objective"]
        base_score = params["base_score"]
        booster = xgb_node.get_booster()
        # The json format was available in October 2017.
        # XGBoost 0.7 was the first version released with it.
        js_tree_list = booster.get_dump(with_stats=True, dump_format = 'json')
        js_trees = [json.loads(s) for s in js_tree_list]
        return objective, base_score, js_trees
        
    @staticmethod
    def _get_default_tree_attribute_pairs(is_classifier):        
        attrs = {}
        for k in {'nodes_treeids',  'nodes_nodeids',
                  'nodes_featureids', 'nodes_modes', 'nodes_values',
                  'nodes_truenodeids', 'nodes_falsenodeids', 'nodes_missing_value_tracks_true'}:
            attrs[k] = []
        if is_classifier:
            for k in {'class_treeids', 'class_nodeids', 'class_ids', 'class_weights'}:
                attrs[k] = []
        else:
            for k in {'target_treeids', 'target_nodeids', 'target_ids', 'target_weights'}:
                attrs[k] = []
        return attrs

    @staticmethod
    def _add_node(attr_pairs, is_classifier, tree_id, tree_weight, node_id, 
                  feature_id, mode, value, true_child_id, false_child_id, weights, weight_id_bias,
                  missing, hitrate):
        if isinstance(feature_id, str):
            # Something like f0, f1...
            if feature_id[0] == "f":
                try:
                    feature_id = int(feature_id[1:])
                except ValueError:
                    raise RuntimeError("Unable to interpret '{0}'".format(feature_id))
            else:
                try:
                    feature_id = int(feature_id)
                except ValueError:
                    raise RuntimeError("Unable to interpret '{0}'".format(feature_id))
                    
        # Split condition for sklearn
        # * if X_ptr[X_sample_stride * i + X_fx_stride * node.feature] <= node.threshold: 
        # * https://github.com/scikit-learn/scikit-learn/blob/master/sklearn/tree/_tree.pyx#L946 
        # Split condition for xgboost 
        # * if (fvalue < split_value) 
        # * https://github.com/dmlc/xgboost/blob/master/include/xgboost/tree_model.h#L804             
    
        attr_pairs['nodes_treeids'].append(tree_id)
        attr_pairs['nodes_nodeids'].append(node_id)
        attr_pairs['nodes_featureids'].append(feature_id)
        attr_pairs['nodes_modes'].append(mode)
        attr_pairs['nodes_values'].append(float(value))
        attr_pairs['nodes_truenodeids'].append(true_child_id)
        attr_pairs['nodes_falsenodeids'].append(false_child_id)
        attr_pairs['nodes_missing_value_tracks_true'].append(missing)
        if 'nodes_hitrates' in attr_pairs:
            attr_pairs['nodes_hitrates'].append(hitrate)
        if mode == 'LEAF':
            if is_classifier:
                for i, w in enumerate(weights):
                    attr_pairs['class_treeids'].append(tree_id)
                    attr_pairs['class_nodeids'].append(node_id)
                    attr_pairs['class_ids'].append(i + weight_id_bias)
                    attr_pairs['class_weights'].append(float(tree_weight * w))
            else:
                for i, w in enumerate(weights):
                    attr_pairs['target_treeids'].append(tree_id)
                    attr_pairs['target_nodeids'].append(node_id)
                    attr_pairs['target_ids'].append(i + weight_id_bias)
                    attr_pairs['target_weights'].append(float(tree_weight * w))
        
    @staticmethod
    def _fill_node_attributes(treeid, tree_weight, jsnode, attr_pairs, is_classifier, remap):
        if 'children' in jsnode:
            XGBConverter._add_node(attr_pairs=attr_pairs, is_classifier=is_classifier, 
                        tree_id=treeid, tree_weight=tree_weight, 
                        value=jsnode['split_condition'], node_id=remap[jsnode['nodeid']], 
                        feature_id=jsnode['split'], 
                        mode='BRANCH_LT', # 'BRANCH_LEQ' --> is for sklearn
                        true_child_id=remap[jsnode['yes']], # ['children'][0]['nodeid'], 
                        false_child_id=remap[jsnode['no']], # ['children'][1]['nodeid'], 
                        weights=None, weight_id_bias=None,
                        missing=jsnode.get('missing', -1) == jsnode['yes'], # ['children'][0]['nodeid'],
                        hitrate=jsnode.get('cover', 0))

            for ch in jsnode['children']:
                if 'children' in ch or 'leaf' in ch:
                    XGBConverter._fill_node_attributes(treeid, tree_weight, ch, attr_pairs, is_classifier, remap)
                else:
                    raise RuntimeError("Unable to convert this node {0}".format(ch))                        
                
        else:
            weights = [jsnode['leaf']]
            weights_id_bias = 0
            XGBConverter._add_node(attr_pairs=attr_pairs, is_classifier=is_classifier, 
                        tree_id=treeid, tree_weight=tree_weight, 
                        value=0., node_id=remap[jsnode['nodeid']], 
                        feature_id=0, mode='LEAF',
                        true_child_id=0, false_child_id=0, 
                        weights=weights, weight_id_bias=weights_id_bias,
                        missing=False, hitrate=jsnode.get('cover', 0))

    @staticmethod
    def _remap_nodeid(jsnode, remap=None):
        if remap is None:
            remap = {}
        nid = jsnode['nodeid']
        remap[nid] = len(remap)
        if 'children' in jsnode:
            for ch in jsnode['children']:
                XGBConverter._remap_nodeid(ch, remap)
        return remap
            
    @staticmethod
    def fill_tree_attributes(js_xgb_node, attr_pairs, tree_weights, is_classifier):
        if not isinstance(js_xgb_node, list):
            raise TypeError("js_xgb_node must be a list")
        for treeid, (jstree, w) in enumerate(zip(js_xgb_node, tree_weights)):
            remap = XGBConverter._remap_nodeid(jstree)
            XGBConverter._fill_node_attributes(treeid, w, jstree, attr_pairs, is_classifier, remap)


class XGBRegressorConverter(XGBConverter):

    @staticmethod
    def validate(xgb_node):
        return XGBConverter.validate(xgb_node)

    @staticmethod
    def _get_default_tree_attribute_pairs():
        attrs = XGBConverter._get_default_tree_attribute_pairs(False)
        attrs['post_transform'] = 'NONE'
        attrs['n_targets'] = 1
        return attrs

    @staticmethod
    def convert(context, xgb_node, inputs):
        objective, base_score, js_trees = XGBConverter.common_members(xgb_node, inputs)
        
        if objective in ["reg:gamma", "reg:tweedie"]:
            raise RuntimeError("Objective '{}' not supported.".format(objective))
        
        booster = xgb_node.get_booster()
        
        attr_pairs = XGBRegressorConverter._get_default_tree_attribute_pairs()
        attr_pairs['base_values'] = [base_score]
        XGBConverter.fill_tree_attributes(js_trees, attr_pairs, [1 for _ in js_trees], False)
        
        nb = NodeBuilder(context, "TreeEnsembleRegressor", op_domain='ai.onnx.ml')
        for k, v in sorted(attr_pairs.items()):
            nb.add_attribute(k, v)
        nb.extend_inputs(inputs)

        output_dim = None
        try:
            if len(inputs[0].type.tensor_type.shape.dim) > 0:
                output_dim = [inputs[0].type.tensor_type.shape.dim[0].dim_value]
        except Exception:
            raise ValueError('Invalid/missing input dimension.')
        nb.add_output(model_util.make_tensor_value_info(nb.name, onnx_proto.TensorProto.FLOAT, output_dim))
        return [nb.make_node()]


class XGBClassifierConverter(XGBConverter):

    @staticmethod
    def validate(xgb_node):
        return XGBConverter.validate(xgb_node)

    @staticmethod
    def _get_default_tree_attribute_pairs():
        attrs = XGBConverter._get_default_tree_attribute_pairs(True)
        # TODO: check it is implemented. The model cannot be loaded when they are present.
        #attrs['nodes_hitrates'] = []
        return attrs

    @staticmethod
    def convert(context, xgb_node, inputs):
        objective, base_score, js_trees = XGBConverter.common_members(xgb_node,  inputs)
        params = XGBConverter.get_xgb_params(xgb_node)
        
        attr_pairs = XGBClassifierConverter._get_default_tree_attribute_pairs()
        XGBConverter.fill_tree_attributes(js_trees, attr_pairs, [1 for _ in js_trees], True)
        
        if len(attr_pairs['class_treeids']) == 0:
            raise RuntimeError("XGBoost model is empty.")
        ncl = (max(attr_pairs['class_treeids']) + 1) // params['n_estimators']
        if ncl <= 1:
            ncl = 2
            # See https://github.com/dmlc/xgboost/blob/master/src/common/math.h#L23.
            attr_pairs['post_transform'] = "LOGISTIC"
            attr_pairs['class_ids'] = [0 for v in attr_pairs['class_treeids']]
        else:
            # See https://github.com/dmlc/xgboost/blob/master/src/common/math.h#L35.
            attr_pairs['post_transform'] = "SOFTMAX"
            # attr_pairs['base_values'] = [base_score for n in range(ncl)]
            attr_pairs['class_ids'] = [v % ncl for v in attr_pairs['class_treeids']]
        class_labels = list(range(ncl))

        attr_pairs['classlabels_int64s'] = class_labels        
        
        nb = NodeBuilder(context, "TreeEnsembleClassifier", op_domain='ai.onnx.ml')
        for k, v in sorted(attr_pairs.items()):
            nb.add_attribute(k, v)
        output_type = onnx_proto.TensorProto.INT64            
            
        if objective == "binary:logistic":
            ncl = 2
        elif objective == "multi:softprob":
            ncl = len(js_trees) // params['n_estimators']
        else:
            raise RuntimeError("Unexpected objective: {0}".format(objective))            

        nb.extend_inputs(inputs)
        output_dim = None
        try:
            if len(inputs[0].type.tensor_type.shape.dim) > 0:
                output_dim = [inputs[0].type.tensor_type.shape.dim[0].dim_value]
        except:
            raise ValueError('Invalid/missing input dimension.')

        output_type = onnx_proto.TensorProto.INT64
        output_y = model_util.make_tensor_value_info(nb.name + '.Y', output_type, output_dim)
        nb.add_output(output_y)
        context.add_output(output_y)

        prob_input = context.get_unique_name('classProbability')
        nb.add_output(prob_input)
        
        appended_node = add_zipmap(prob_input, output_type, class_labels, context)
        return [nb.make_node(), appended_node]


register_converter(XGBRegressor, XGBRegressorConverter)
register_converter(XGBClassifier, XGBClassifierConverter)
