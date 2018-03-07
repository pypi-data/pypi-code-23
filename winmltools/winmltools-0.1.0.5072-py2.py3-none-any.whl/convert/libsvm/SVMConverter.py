#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from ...proto import onnx_proto
from ..common import register_converter
from ..common import utils
from ..common import NodeBuilder
from ..common import model_util
from ..sklearn import add_zipmap

import svm
import svmutil
import numpy


class SVMConverter:
    """
    Converts a SVM model trained with *svmlib*.
    """
    @staticmethod
    def validate(svm_node):
        try:
            utils._check_has_attr(svm_node, 'param')
            utils._check_has_attr(svm_node, 'SV')
            utils._check_has_attr(svm_node, 'nSV')
            utils._check_has_attr(svm_node, 'sv_coef')
            utils._check_has_attr(svm_node, 'l')
            utils._check_has_attr(svm_node.param, 'gamma')
            utils._check_has_attr(svm_node.param, 'coef0')
            utils._check_has_attr(svm_node.param, 'degree')
            utils._check_has_attr(svm_node.param, 'kernel_type')
            utils._check_has_attr(svm_node, 'rho')
        except AttributeError as e:
            raise RuntimeError("Missing type from svm node:" + str(e))

            
    @staticmethod
    def get_sv(svm_node):
        labels = svm_node.get_labels()
        sv = svm_node.get_SV()
        if len(sv) == 0:
            raise RuntimeError("No support vector machine. This usually happens with very small datasets or the training failed.")

        maxk = max(max(row.keys() for row in sv))
        mat = numpy.zeros((len(sv), maxk+1), dtype=numpy.float32)
        
        for i, row in enumerate(sv):
            for k,v in row.items():
                if k == -1:
                    k = 0
                try:
                    mat[i, k] = v
                except IndexError:
                    raise RuntimeError("Issue with one dimension\nlabels={0}\n#sv={1}\nshape={2}\npos={3}x{4}-maxk={5}-svm.l={6}\nrow={7}".format(labels, nsv, mat.shape, i, k, maxk, svm_node.l, row))
        # We do not consider the first row (class -1).
        mat = mat[:, 1:]
        
        # mat.shape should be (n_vectors, X.shape[1])
        # where X.shape[1] is the number of features.
        # However, it can be <= X.shape.[1] if the last
        # every coefficient is null on the last column.
        # To fix that, an extra parameter must be added to
        # the convert function as there is no way to guess
        # that information from svmlib model.
        return numpy.array(mat.ravel(), dtype=float)

    @staticmethod
    def convert(context, svm_node, inputs, model_name, nb_class):
        kt = svm_node.param.kernel_type
        if kt == svm.RBF:
            kt = 'RBF'
        elif kt == svm.SIGMOID:
            kt = 'SIGMOID'
        elif kt == svm.POLY:
            kt = 'POLY'
        elif kt == svm.LINEAR:
            kt = "LINEAR"
        else:
            raise RuntimeError("Unexpected value for kernel: {0}".format(kt))

        def copy_sv_coef(sv_coef):
            nrc = svm_node.nr_class-1
            res = numpy.zeros((svm_node.l, nrc), dtype=numpy.float64)
            for i in range(0, svm_node.l):
                for j in range(nrc):
                    res[i, j] = svm_node.sv_coef[j][i]
            return res.T
            
        if nb_class > 2:
            # See above.
            coef = copy_sv_coef(svm_node.sv_coef)
        else:
            coef = numpy.array(svm_node.get_sv_coef()).ravel()
        
        atts = dict(kernel_type=kt,
                    kernel_params=[float(_) for _ in [svm_node.param.gamma, svm_node.param.coef0, svm_node.param.degree]],
                    coefficients=list(coef.ravel()))

        nb = NodeBuilder(context, model_name, op_domain='ai.onnx.ml')
        for k, v in atts.items():
            nb.add_attribute(k, v)

        nb.extend_inputs(inputs)
        return nb


class SVCConverter(SVMConverter):
    
    @staticmethod
    def validate(svm_node):
        SVMConverter.validate(svm_node)
        try:
            utils._check_has_attr(svm_node, 'probA')
            utils._check_has_attr(svm_node, 'probB')
        except AttributeError as e:
            raise RuntimeError("Missing type from svm node:" + str(e))
    
    @staticmethod
    def convert(context, svm_node, inputs):
        nbclass = len(svm_node.get_labels())
        # See converter for sklearn.
        nb = SVMConverter.convert(context, svm_node, inputs, "SVMClassifier", nbclass)
        sign_rho = -1.
        sign_coef = 1.
        
        if svm_node.is_probability_model():
            st = svm_node.param.svm_type
            if st == svm.C_SVC or st == svm.NU_SVC:
                n_class = len(svm_node.get_labels())
                n = int(n_class*(n_class-1)/2)
                probA = [svm_node.probA[i] for i in range(n)]
                probB = [svm_node.probB[i] for i in range(n)]
                nb.add_attribute("prob_a", probA)
                nb.add_attribute("prob_b", probB)            
                nb.add_attribute('rho', [svm_node.rho[i] * sign_rho for i in range(n)])
            else:
                nb.add_attribute('rho', [svm_node.rho[0] * sign_rho])
        else:
            nb.add_attribute('rho', [svm_node.rho[0] * sign_rho])
            
        class_labels = utils.cast_list(int, svm_node.get_labels())
        # Predictions are different when label are not sorted (multi-classification).
        class_labels.sort()
        nb.add_attribute('classlabels_ints', class_labels)
        output_type = onnx_proto.TensorProto.INT64

        output_y = model_util.make_tensor_value_info(nb.name, output_type, [1,1])
        nb.add_output(output_y)
        context.add_output(output_y)
            
        nbclass = len(svm_node.get_labels())
        nb.add_attribute('vectors_per_class', [svm_node.nSV[i] for i in range(nbclass)])
        nb.add_attribute('post_transform', "NONE")
        nb.add_attribute('support_vectors', SVCConverter.get_sv(svm_node))
        
        # Add a vec dictionizer to handle the map output
        prob_input = context.get_unique_name('classProbability')
        nb.add_output(prob_input)

        # Helps comparing scikit-learn SVM with svmlib.
        # We should have a function which reverse-engineers a node
        # and displays the attributes.
        # import pprint
        # print('--SVC')
        # pprint.pprint(nb._attributes)

        appended_node = add_zipmap(prob_input, output_type, class_labels, context)
        return [nb.make_node(), appended_node]


class SVRConverter(SVMConverter):

    @staticmethod
    def validate(svm_node):
        SVMConverter.validate(svm_node)
        try:
            utils._check_has_attr(svm_node, 'l')
        except AttributeError as e:
            raise RuntimeError("Missing type from svm node:" + str(e))
    
    @staticmethod
    def convert(context, svm_node, inputs):
        nb = SVMConverter.convert(context, svm_node, inputs, "SVMRegressor", 0)
        
        nb.add_attribute("n_supports", svm_node.l)
        nb.add_attribute('post_transform', "NONE")
        nb.add_attribute('rho', [-svm_node.rho[0]])
        output_dim = None
        try:
            if len(inputs[0].type.tensor_type.shape.dim) > 0:
                output_dim = [1, inputs[0].type.tensor_type.shape.dim[0].dim_value]
        except Exception as e:
            raise ValueError('Invalid/missing input dimension.') from e
        nb.add_attribute('support_vectors', SVCConverter.get_sv(svm_node))
        nb.add_output(model_util.make_tensor_value_info(nb.name, onnx_proto.TensorProto.FLOAT, output_dim))

        return [nb.make_node()]
    

class AnyLibSvmConverter:
    
    @staticmethod
    def select(svm_node):
        if svm_node.param.svm_type in (svm.C_SVC, svm.NU_SVC):
            return SVCConverter
        if svm_node.param.svm_type in (svm.EPSILON_SVR, svm.NU_SVR):
            return SVRConverter
        raise RuntimeError("svm_node type is unexpected '{0}'".format(svm_node.param.svm_type))
    
    @staticmethod
    def validate(svm_node):
        sel = AnyLibSvmConverter.select(svm_node)
        sel.validate(svm_node)
    
    @staticmethod
    def convert(context, svm_node, inputs):
        sel = AnyLibSvmConverter.select(svm_node)
        return sel.convert(context, svm_node, inputs)


# Register the class for processing
register_converter(svm.svm_model, AnyLibSvmConverter)

