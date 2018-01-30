# references: 
# https://gitlab.com/datadrivendiscovery/common-primitives/blob/devel/common_primitives/logistic_regression.py

import os.path
import typing
from uuid import uuid4, uuid3, NAMESPACE_DNS

from d3m_metadata import container, hyperparams, metadata as metadata_module, params, utils
from d3m_metadata.container.numpy import ndarray
from primitive_interfaces import base, supervised_learning

from . import __version__

__all__ = ('TensorMachinesBinaryClassification')

# ninputs by ndimensions array of floats
Inputs = ndarray
# 1D array of length ninputs
Outputs = ndarray

Input = ndarray
Output = int

class Params(params.Params):
    weights : ndarray
    norms : ndarray # used in preprocessing

class Hyperparams(hyperparams.Hyperparams):
    # search over these hyperparameters to tune performance
    q = hyperparams.UniformInt(default=3, lower=2, upper=9, description="degree of the polynomial to be fit", semantic_types=['https://metadata.datadrivendiscovery.org/types/TuningParameter'])
    r = hyperparams.UniformInt(default=5, lower=2, upper=10, description="rank of the coefficient tensors to be fit", semantic_types=['https://metadata.datadrivendiscovery.org/types/TuningParameter'])
    gamma = hyperparams.LogUniform(default=.01, lower=.0001, upper=10, description="l2 regularization to use on the tensor low-rank factors", semantic_types=['https://metadata.datadrivendiscovery.org/types/TuningParameter'])
    alpha = hyperparams.LogUniform(default=.1, lower=.001, upper=1, description="variance of the random initialization of the factors", semantic_types=['https://metadata.datadrivendiscovery.org/types/TuningParameter'])
    epochs = hyperparams.UniformInt(default=30, lower=15, upper=100, description="maximum iterations of LBFGS, or number of epochs of SFO", semantic_types=['https://metadata.datadrivendiscovery.org/types/TuningParameter'])

    # control parameters determined once during pipeline building then fixed
    solver = hyperparams.Enumeration(default="LBFGS", values=["SFO", "LBFGS"], description="solver to use: LBFGS better for small enough datasets, SFO does minibached stochastic quasi-Newton to scale to large dataset", semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'])
    preprocess = hyperparams.Enumeration(default="YES", values=["YES", "NO"], description="whether to use a preprocessing that tends to work well for tensor machines", semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'])


class TensorMachinesBinaryClassification(supervised_learning.SupervisedLearnerPrimitiveBase[Inputs, Outputs, Params, Hyperparams]):
    """
    Fits a polynomial regression model to perform logistic regression of +-1 targets.
    Operates by considering the polynomial's coefficients as a tensor, then learning 
    an l2 regularized low-rank factorization of the coefficients. Think of as learning
    Kar--Karnick type polynomial features, but through optimization rather than randomization.
    """

    __author__ = "ICSI" # a la directions on https://gitlab.datadrivendiscovery.org/jpl/primitives_repo
    metadata = metadata_module.PrimitiveMetadata({
        'id': 'ecc83605-d340-490d-9a2d-81c2ea6cb6cb', #uuid3(NAMESPACE_DNS, "realML.kernel.TensorMachineBinaryClassification" + __version__),
        'version': __version__,
        'name': 'Tensor Machine Binary Classifier',
        'keywords' : ['kernel learning', 'binary classification', 'adaptive features', 'polynomial model', 'classification'],
        'source' : {
            'name': __author__,
            'contact': 'mailto:gittea@rpi.edu',
            'citation': 'https://arxiv.org/abs/1504.01697'
        },
        'installation': [
            {
                'type': metadata_module.PrimitiveInstallationType.PIP,
                'package': 'realML',
                'version': __version__
            }
        ],
        'location_uris': [ # NEED TO REF SPECIFIC COMMIT
            'https://github.com/alexgittens/realML/blob/master/realML/kernel/TensorMachinesBinaryClassification.py',
            ],
        'python_path': 'd3m.primitives.realML.kernel.TensorMachineBinaryClassification',
        'algorithm_types' : [
            metadata_module.PrimitiveAlgorithmType.LOGISTIC_REGRESSION,
        ],
        'primitive_family': metadata_module.PrimitiveFamily.CLASSIFICATION,
        'preconditions': [
            metadata_module.PrimitivePrecondition.NO_MISSING_VALUES,
            metadata_module.PrimitivePrecondition.NO_CATEGORICAL_VALUES
        ]
    })

def __init__(self, *, hyperparams: Hyperparams, random_seed: int = 0, docker_containers: typing.Dict[str, str] = None) -> None:
    super().__init__(hyperparams=hyperparams, random_seed=random_seed, docker_containers=docker_containers)
    self._seed = random_seed
    self._fitted = False
    self._training_inputs = None
    self._training_outputs = None
    self._weights = None

def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> base.CallResult[Outputs]:
    if self._w is None:
        raise ValueError("Calling produce before fitting.")

    z = tm_predict(self._weights, inputs, self.hyperparams['q'], self.hyperparams['r'], 'bc')
    return CallResult(z.astype(int))

def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
    self._training_inputs = inputs
    self._training_outputs = outputs
    self._fitted = False

def fit(self, *, timeout: float = None, iterations: int = None) -> base.CallResult[None]:
    if self._fitted:
        return base.CallResult(None)

    if not self._training_inputs or not self._training_inputs:
        raise ValueError("Missing training data.")

    (self._weights, _) = tm.fit(self._training_inputs, self._training_outputs, 'bc', self.hyperparams['r'],
           self.hyperparams['q'], self.hyperparams['gamma'], self.hyperparams['solver'],
           self.hyperparams['epochs'], self.hyperparams['alpha'], seed=self._seed)
    
    self._fitted = True
    return base.CallResult(None)

def get_params(self) -> Params:
    return Params(weights=self._weights)

def set_params(self, *, params: Params) -> None:
    self._weights = params['weights']

def set_random_seed(self, *, seed: int) -> None:
    self._seed = seed


