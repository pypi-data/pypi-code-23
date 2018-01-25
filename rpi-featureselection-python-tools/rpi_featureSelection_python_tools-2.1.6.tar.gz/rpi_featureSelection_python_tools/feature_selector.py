import os, sys
# from typing import NamedTuple, Union, List, Sequence, Any, Dict
import typing
import scipy.io
import numpy as np

# from d3m_metadata.container.numpy import ndarray
# from d3m_metadata import hyperparams, params
from d3m_metadata import container, hyperparams, metadata as metadata_module, params, utils
from primitive_interfaces.supervised_learning import SupervisedLearnerPrimitiveBase
from primitive_interfaces.base import CallResult
# from . import __version__


import rpi_feature_selection_toolbox


Inputs = container.ndarray
Outputs = container.ndarray

__all__ = ('IPCMBplus_Selector',)

class Params(params.Params):
    pass
#    n_features: int
#    feature_index: ndarray


class Hyperparams(hyperparams.Hyperparams):
    pass
    '''
    n_bins = hyperparams.UniformInt(
                            lower=5,
                            upper=15,
                            default=10,
                            description='The maximum number of bins used for continuous variables discretization.'
                            )
    '''


class IPCMBplus_Selector(SupervisedLearnerPrimitiveBase[Inputs, Outputs, Params, Hyperparams]):

    metadata = metadata_module.PrimitiveMetadata({
        'id': '69845479-0b61-3578-b382-972cd0e61d69',
        'version': '2.1.2',
        'name': 'IPCMB feature selector',
        'keywords': ['rpi primitives'],
        'source': {
            'name': 'RPI'
        },
        'installation':[
            {
                'type': 'PIP',
                'package': 'rpi_feature_selection_toolbox',
                'version': '2.0.4'
            },
            {
                'type': 'PIP',
                'package': 'rpi_featureSelection_python_tools',
	            'version': '2.1.6'
            }
        ],
        'python_path': 'd3m.primitives.rpi_featureSelection_python_tools.IPCMBplus_Selector',
        'algorithm_types': ['MINIMUM_REDUNDANCY_FEATURE_SELECTION'],
        'primitive_family': 'FEATURE_SELECTION',
        'preconditions': [
            "NO_CATEGORICAL_VALUES",
            "NO_MISSING_VALUES"
        ]
    })


    def __init__(self, *, hyperparams: Hyperparams, random_seed: int = 0, docker_containers: typing.Dict[str, str] = None) -> None:
        super().__init__(hyperparams=hyperparams, random_seed=random_seed, docker_containers=docker_containers)
        self._index = None
        self._training_inputs = None
        self._training_outputs = None
        self._fitted = False

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        self._training_inputs = inputs
        self._training_outputs = outputs
        self._fitted = False


    def fit(self, *, timeout: float = None, iterations: int = None) -> None:
        if self._fitted:
            return CallResult(None)

        if self._training_inputs.any() == None or self._training_outputs.any() == None: 
            raise ValueError('Missing training data, or missing values exist.')

        scipy.io.savemat('rpi_data.mat', mdict={'traindata': self._training_inputs, 'trainlabel': self._training_outputs})

        a = rpi_feature_selection_toolbox.initialize()
        index = np.reshape(np.array(a.IPCMBplus()), [-1, ])

        self._index = (index - 1).astype(int)
        self._fitted = True

        os.remove('rpi_data.mat')

        return CallResult(None)


    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> Outputs:  # inputs: m x n numpy array
        if self._fitted:
            return CallResult(inputs[:, self._index])
        else:
            raise ValueError('Model should be fitted first.')


    def get_params(self) -> None:
        pass


    def set_params(self) -> None:
        pass



class JMIplus_Selector(SupervisedLearnerPrimitiveBase[Inputs, Outputs, Params, Hyperparams]):

    metadata = metadata_module.PrimitiveMetadata({
        'id': '58a8fe68-74eb-3e21-a823-bfa708010759',
        'version': '2.1.2',
        'name': 'JMIplus feature selector',
        'keywords': ['rpi primitives'],
        'source': {
            'name': 'RPI'
        },
        'installation':[
            {
                'type': 'PIP',
                'package': 'rpi_feature_selection_toolbox',
                'version': '2.0.4'
            },
            {
                'type': 'PIP',
                'package': 'rpi_featureSelection_python_tools',
	            'version': '2.1.6'
            }
        ],
        'python_path': 'd3m.primitives.rpi_featureSelection_python_tools.JMIplus_Selector',
        'algorithm_types': ['MINIMUM_REDUNDANCY_FEATURE_SELECTION'],
        'primitive_family': 'FEATURE_SELECTION',
        'preconditions': [
            "NO_CATEGORICAL_VALUES",
            "NO_MISSING_VALUES"
        ]
    })


    def __init__(self, *, hyperparams: Hyperparams, random_seed: int = 0, docker_containers: typing.Dict[str, str] = None) -> None:
        super().__init__(hyperparams=hyperparams, random_seed=random_seed, docker_containers=docker_containers)
        self._index = None
        self._training_inputs = None
        self._training_outputs = None
        self._fitted = False

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        self._training_inputs = inputs
        self._training_outputs = outputs
        self._fitted = False


    def fit(self, *, timeout: float = None, iterations: int = None) -> None:
        if self._fitted:
            return CallResult(None)

        if self._training_inputs.any() == None or self._training_outputs.any() == None: 
            raise ValueError('Missing training data, or missing values exist.')

        scipy.io.savemat('rpi_data.mat', mdict={'traindata': self._training_inputs, 'trainlabel': self._training_outputs})

        a = rpi_feature_selection_toolbox.initialize()
        index = np.reshape(np.array(a.JMIplus()), [-1, ])

        self._index = (index - 1).astype(int)
        self._fitted = True

        os.remove('rpi_data.mat')

        return CallResult(None)


    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> Outputs:  # inputs: m x n numpy array
        if self._fitted:
            return CallResult(inputs[:, self._index])
        else:
            raise ValueError('Model should be fitted first.')


    def get_params(self) -> None:
        pass


    def set_params(self) -> None:
        pass



class STMBplus_Selector(SupervisedLearnerPrimitiveBase[Inputs, Outputs, Params, Hyperparams]):

    metadata = metadata_module.PrimitiveMetadata({
        'id': '9d1a2e58-5f97-386c-babd-5a9b4e9b6d6c',
        'version': '2.1.2',
        'name': 'STMBplus feature selector',
        'keywords': ['rpi primitives'],
        'source': {
            'name': 'RPI'
        },
        'installation':[
            {
                'type': 'PIP',
                'package': 'rpi_feature_selection_toolbox',
                'version': '2.0.4'
            },
            {
                'type': 'PIP',
                'package': 'rpi_featureSelection_python_tools',
	            'version': '2.1.6'
            }
        ],
        'python_path': 'd3m.primitives.rpi_featureSelection_python_tools.STMBplus_Selector',
        'algorithm_types': ['MINIMUM_REDUNDANCY_FEATURE_SELECTION'],
        'primitive_family': 'FEATURE_SELECTION',
        'preconditions': [
            "NO_CATEGORICAL_VALUES",
            "NO_MISSING_VALUES"
        ]
    })


    def __init__(self, *, hyperparams: Hyperparams, random_seed: int = 0, docker_containers: typing.Dict[str, str] = None) -> None:
        super().__init__(hyperparams=hyperparams, random_seed=random_seed, docker_containers=docker_containers)
        self._index = None
        self._training_inputs = None
        self._training_outputs = None
        self._fitted = False

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        self._training_inputs = inputs
        self._training_outputs = outputs
        self._fitted = False


    def fit(self, *, timeout: float = None, iterations: int = None) -> None:
        if self._fitted:
            return CallResult(None)

        if self._training_inputs.any() == None or self._training_outputs.any() == None: 
            raise ValueError('Missing training data, or missing values exist.')

        scipy.io.savemat('rpi_data.mat', mdict={'traindata': self._training_inputs, 'trainlabel': self._training_outputs})

        a = rpi_feature_selection_toolbox.initialize()
        index = np.reshape(np.array(a.STMBplus()), [-1, ])

        self._index = (index - 1).astype(int)
        self._fitted = True

        os.remove('rpi_data.mat')

        return CallResult(None)


    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> Outputs:  # inputs: m x n numpy array
        if self._fitted:
            return CallResult(inputs[:, self._index])
        else:
            raise ValueError('Model should be fitted first.')


    def get_params(self) -> None:
        pass


    def set_params(self) -> None:
        pass



class aSTMBplus_Selector(SupervisedLearnerPrimitiveBase[Inputs, Outputs, Params, Hyperparams]):

    metadata = metadata_module.PrimitiveMetadata({
        'id': '744687e8-2224-3ef5-92e5-ce66d2ad05d7',
        'version': '2.1.2',
        'name': 'aSTMBplus feature selector',
        'keywords': ['rpi primitives'],
        'source': {
            'name': 'RPI'
        },
        'installation':[
            {
                'type': 'PIP',
                'package': 'rpi_feature_selection_toolbox',
                'version': '2.0.4'
            },
            {
                'type': 'PIP',
                'package': 'rpi_featureSelection_python_tools',
	            'version': '2.1.6'
            }
        ],
        'python_path': 'd3m.primitives.rpi_featureSelection_python_tools.aSTMBplus_Selector',
        'algorithm_types': ['MINIMUM_REDUNDANCY_FEATURE_SELECTION'],
        'primitive_family': 'FEATURE_SELECTION',
        'preconditions': [
            "NO_CATEGORICAL_VALUES",
            "NO_MISSING_VALUES"
        ]
    })


    def __init__(self, *, hyperparams: Hyperparams, random_seed: int = 0, docker_containers: typing.Dict[str, str] = None) -> None:
        super().__init__(hyperparams=hyperparams, random_seed=random_seed, docker_containers=docker_containers)
        self._index = None
        self._training_inputs = None
        self._training_outputs = None
        self._fitted = False

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        self._training_inputs = inputs
        self._training_outputs = outputs
        self._fitted = False


    def fit(self, *, timeout: float = None, iterations: int = None) -> None:
        if self._fitted:
            return CallResult(None)

        if self._training_inputs.any() == None or self._training_outputs.any() == None: 
            raise ValueError('Missing training data, or missing values exist.')

        scipy.io.savemat('rpi_data.mat', mdict={'traindata': self._training_inputs, 'trainlabel': self._training_outputs})

        a = rpi_feature_selection_toolbox.initialize()
        index = np.reshape(np.array(a.aSTMBplus()), [-1, ])

        self._index = (index - 1).astype(int)
        self._fitted = True

        os.remove('rpi_data.mat')

        return CallResult(None)


    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> Outputs:  # inputs: m x n numpy array
        if self._fitted:
            return CallResult(inputs[:, self._index])
        else:
            raise ValueError('Model should be fitted first.')


    def get_params(self) -> None:
        pass


    def set_params(self) -> None:
        pass



class sSTMBplus_Selector(SupervisedLearnerPrimitiveBase[Inputs, Outputs, Params, Hyperparams]):

    metadata = metadata_module.PrimitiveMetadata({
        'id': '976060b2-fb0a-329a-8851-d22b25ebe99a',
        'version': '2.1.2',
        'name': 'sSTMBplus feature selector',
        'keywords': ['rpi primitives'],
        'source': {
            'name': 'RPI'
        },
        'installation':[
            {
                'type': 'PIP',
                'package': 'rpi_feature_selection_toolbox',
                'version': '2.0.4'
            },
            {
                'type': 'PIP',
                'package': 'rpi_featureSelection_python_tools',
	            'version': '2.1.6'
            }
        ],
        'python_path': 'd3m.primitives.rpi_featureSelection_python_tools.sSTMBplus_Selector',
        'algorithm_types': ['MINIMUM_REDUNDANCY_FEATURE_SELECTION'],
        'primitive_family': 'FEATURE_SELECTION',
        'preconditions': [
            "NO_CATEGORICAL_VALUES",
            "NO_MISSING_VALUES"
        ]
    })


    def __init__(self, *, hyperparams: Hyperparams, random_seed: int = 0, docker_containers: typing.Dict[str, str] = None) -> None:
        super().__init__(hyperparams=hyperparams, random_seed=random_seed, docker_containers=docker_containers)
        self._index = None
        self._training_inputs = None
        self._training_outputs = None
        self._fitted = False

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        self._training_inputs = inputs
        self._training_outputs = outputs
        self._fitted = False


    def fit(self, *, timeout: float = None, iterations: int = None) -> None:
        if self._fitted:
            return CallResult(None)

        if self._training_inputs.any() == None or self._training_outputs.any() == None: 
            raise ValueError('Missing training data, or missing values exist.')

        scipy.io.savemat('rpi_data.mat', mdict={'traindata': self._training_inputs, 'trainlabel': self._training_outputs})

        a = rpi_feature_selection_toolbox.initialize()
        index = np.reshape(np.array(a.sSTMBplus()), [-1, ])

        self._index = (index - 1).astype(int)
        self._fitted = True

        os.remove('rpi_data.mat')

        return CallResult(None)


    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> Outputs:  # inputs: m x n numpy array
        if self._fitted:
            return CallResult(inputs[:, self._index])
        else:
            raise ValueError('Model should be fitted first.')


    def get_params(self) -> None:
        pass


    def set_params(self) -> None:
        pass



class pSTMB_Selector(SupervisedLearnerPrimitiveBase[Inputs, Outputs, Params, Hyperparams]):

    metadata = metadata_module.PrimitiveMetadata({
        'id': '616e087e-1bc8-3884-8675-3420bce832d5',
        'version': '2.1.2',
        'name': 'pSTMB feature selector',
        'keywords': ['rpi primitives'],
        'source': {
            'name': 'RPI'
        },
        'installation':[
            {
                'type': 'PIP',
                'package': 'rpi_feature_selection_toolbox',
                'version': '2.0.4'
            },
            {
                'type': 'PIP',
                'package': 'rpi_featureSelection_python_tools',
	            'version': '2.1.6'
            }
        ],
        'python_path': 'd3m.primitives.rpi_featureSelection_python_tools.pSTMB_Selector',
        'algorithm_types': ['MINIMUM_REDUNDANCY_FEATURE_SELECTION'],
        'primitive_family': 'FEATURE_SELECTION',
        'preconditions': [
            "NO_CATEGORICAL_VALUES",
            "NO_MISSING_VALUES"
        ]
    })


    def __init__(self, *, hyperparams: Hyperparams, random_seed: int = 0, docker_containers: typing.Dict[str, str] = None) -> None:
        super().__init__(hyperparams=hyperparams, random_seed=random_seed, docker_containers=docker_containers)
        self._index = None
        self._training_inputs = None
        self._training_outputs = None
        self._fitted = False

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        self._training_inputs = inputs
        self._training_outputs = outputs
        self._fitted = False


    def fit(self, *, timeout: float = None, iterations: int = None) -> None:
        if self._fitted:
            return CallResult(None)

        if self._training_inputs.any() == None or self._training_outputs.any() == None: 
            raise ValueError('Missing training data, or missing values exist.')

        scipy.io.savemat('rpi_data.mat', mdict={'traindata': self._training_inputs, 'trainlabel': self._training_outputs})

        a = rpi_feature_selection_toolbox.initialize()
        index = np.reshape(np.array(a.pSTMB()), [-1, ])

        self._index = (index - 1).astype(int)
        self._fitted = True

        os.remove('rpi_data.mat')

        return CallResult(None)


    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> Outputs:  # inputs: m x n numpy array
        if self._fitted:
            return CallResult(inputs[:, self._index])
        else:
            raise ValueError('Model should be fitted first.')


    def get_params(self) -> None:
        pass


    def set_params(self) -> None:
        pass


class F_STMB_Selector(SupervisedLearnerPrimitiveBase[Inputs, Outputs, Params, Hyperparams]):

    metadata = metadata_module.PrimitiveMetadata({
        'id': '37079f49-54d5-3d47-a221-5664c546ff90',
        'version': '2.1.2',
        'name': 'F_STMB feature selector',
        'keywords': ['rpi primitives'],
        'source': {
            'name': 'RPI'
        },
        'installation':[
            {
                'type': 'PIP',
                'package': 'rpi_feature_selection_toolbox',
                'version': '2.0.4'
            },
            {
                'type': 'PIP',
                'package': 'rpi_featureSelection_python_tools',
	            'version': '2.1.6'
            }
        ],
        'python_path': 'd3m.primitives.rpi_featureSelection_python_tools.F_STMB_Selector',
        'algorithm_types': ['MINIMUM_REDUNDANCY_FEATURE_SELECTION'],
        'primitive_family': 'FEATURE_SELECTION',
        'preconditions': [
            "NO_CATEGORICAL_VALUES",
            "NO_MISSING_VALUES"
        ]
    })


    def __init__(self, *, hyperparams: Hyperparams, random_seed: int = 0, docker_containers: typing.Dict[str, str] = None) -> None:
        super().__init__(hyperparams=hyperparams, random_seed=random_seed, docker_containers=docker_containers)
        self._index = None
        self._training_inputs = None
        self._training_outputs = None
        self._fitted = False

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        self._training_inputs = inputs
        self._training_outputs = outputs
        self._fitted = False


    def fit(self, *, timeout: float = None, iterations: int = None) -> None:
        if self._fitted:
            return CallResult(None)

        if self._training_inputs.any() == None or self._training_outputs.any() == None: 
            raise ValueError('Missing training data, or missing values exist.')

        scipy.io.savemat('rpi_data.mat', mdict={'traindata': self._training_inputs, 'trainlabel': self._training_outputs})

        a = rpi_feature_selection_toolbox.initialize()
        index = np.reshape(np.array(a.F_STMB()), [-1, ])

        self._index = (index - 1).astype(int)
        self._fitted = True

        os.remove('rpi_data.mat')

        return CallResult(None)


    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> Outputs:  # inputs: m x n numpy array
        if self._fitted:
            return CallResult(inputs[:, self._index])
        else:
            raise ValueError('Model should be fitted first.')


    def get_params(self) -> None:
        pass


    def set_params(self) -> None:
        pass




class F_aSTMB_Selector(SupervisedLearnerPrimitiveBase[Inputs, Outputs, Params, Hyperparams]):

    metadata = metadata_module.PrimitiveMetadata({
        'id': 'e6217c3c-b2d2-3e6b-82e9-060ffd0b9faf',
        'version': '2.1.2',
        'name': 'F_aSTMB feature selector',
        'keywords': ['rpi primitives'],
        'source': {
            'name': 'RPI'
        },
        'installation':[
            {
                'type': 'PIP',
                'package': 'rpi_feature_selection_toolbox',
                'version': '2.0.4'
            },
            {
                'type': 'PIP',
                'package': 'rpi_featureSelection_python_tools',
	            'version': '2.1.6'
            }
        ],
        'python_path': 'd3m.primitives.rpi_featureSelection_python_tools.F_aSTMB_Selector',
        'algorithm_types': ['MINIMUM_REDUNDANCY_FEATURE_SELECTION'],
        'primitive_family': 'FEATURE_SELECTION',
        'preconditions': [
            "NO_CATEGORICAL_VALUES",
            "NO_MISSING_VALUES"
        ]
    })


    def __init__(self, *, hyperparams: Hyperparams, random_seed: int = 0, docker_containers: typing.Dict[str, str] = None) -> None:
        super().__init__(hyperparams=hyperparams, random_seed=random_seed, docker_containers=docker_containers)
        self._index = None
        self._training_inputs = None
        self._training_outputs = None
        self._fitted = False

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        self._training_inputs = inputs
        self._training_outputs = outputs
        self._fitted = False


    def fit(self, *, timeout: float = None, iterations: int = None) -> None:
        if self._fitted:
            return CallResult(None)

        if self._training_inputs.any() == None or self._training_outputs.any() == None: 
            raise ValueError('Missing training data, or missing values exist.')

        scipy.io.savemat('rpi_data.mat', mdict={'traindata': self._training_inputs, 'trainlabel': self._training_outputs})

        a = rpi_feature_selection_toolbox.initialize()
        index = np.reshape(np.array(a.F_aSTMB()), [-1, ])

        self._index = (index - 1).astype(int)
        self._fitted = True

        os.remove('rpi_data.mat')

        return CallResult(None)


    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> Outputs:  # inputs: m x n numpy array
        if self._fitted:
            return CallResult(inputs[:, self._index])
        else:
            raise ValueError('Model should be fitted first.')


    def get_params(self) -> None:
        pass


    def set_params(self) -> None:
        pass



class F_sSTMB_Selector(SupervisedLearnerPrimitiveBase[Inputs, Outputs, Params, Hyperparams]):

    metadata = metadata_module.PrimitiveMetadata({
        'id': '6285b9fb-26e9-3979-a422-c126ff9448d1',
        'version': '2.1.2',
        'name': 'F_sSTMB feature selector',
        'keywords': ['rpi primitives'],
        'source': {
            'name': 'RPI'
        },
        'installation':[
            {
                'type': 'PIP',
                'package': 'rpi_feature_selection_toolbox',
                'version': '2.0.4'
            },
            {
                'type': 'PIP',
                'package': 'rpi_featureSelection_python_tools',
	            'version': '2.1.6'
            }
        ],
        'python_path': 'd3m.primitives.rpi_featureSelection_python_tools.F_sSTMB_Selector',
        'algorithm_types': ['MINIMUM_REDUNDANCY_FEATURE_SELECTION'],
        'primitive_family': 'FEATURE_SELECTION',
        'preconditions': [
            "NO_CATEGORICAL_VALUES",
            "NO_MISSING_VALUES"
        ]
    })


    def __init__(self, *, hyperparams: Hyperparams, random_seed: int = 0, docker_containers: typing.Dict[str, str] = None) -> None:
        super().__init__(hyperparams=hyperparams, random_seed=random_seed, docker_containers=docker_containers)
        self._index = None
        self._training_inputs = None
        self._training_outputs = None
        self._fitted = False

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        self._training_inputs = inputs
        self._training_outputs = outputs
        self._fitted = False


    def fit(self, *, timeout: float = None, iterations: int = None) -> None:
        if self._fitted:
            return CallResult(None)

        if self._training_inputs.any() == None or self._training_outputs.any() == None: 
            raise ValueError('Missing training data, or missing values exist.')

        scipy.io.savemat('rpi_data.mat', mdict={'traindata': self._training_inputs, 'trainlabel': self._training_outputs})

        a = rpi_feature_selection_toolbox.initialize()
        index = np.reshape(np.array(a.F_sSTMB()), [-1, ])

        self._index = (index - 1).astype(int)
        self._fitted = True

        os.remove('rpi_data.mat')

        return CallResult(None)


    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> Outputs:  # inputs: m x n numpy array
        if self._fitted:
            return CallResult(inputs[:, self._index])
        else:
            raise ValueError('Model should be fitted first.')


    def get_params(self) -> None:
        pass


    def set_params(self) -> None:
        pass



class JMIp_Selector(SupervisedLearnerPrimitiveBase[Inputs, Outputs, Params, Hyperparams]):

    metadata = metadata_module.PrimitiveMetadata({
        'id': 'd332d583-562f-374b-9737-d5d9c2208358',
        'version': '2.1.2',
        'name': 'JMIp feature selector',
        'keywords': ['rpi primitives'],
        'source': {
            'name': 'RPI'
        },
        'installation':[
            {
                'type': 'PIP',
                'package': 'rpi_feature_selection_toolbox',
                'version': '2.0.4'
            },
            {
                'type': 'PIP',
                'package': 'rpi_featureSelection_python_tools',
	            'version': '2.1.6'
            }
        ],
        'python_path': 'd3m.primitives.rpi_featureSelection_python_tools.JMIp_Selector',
        'algorithm_types': ['MINIMUM_REDUNDANCY_FEATURE_SELECTION'],
        'primitive_family': 'FEATURE_SELECTION',
        'preconditions': [
            "NO_CATEGORICAL_VALUES",
            "NO_MISSING_VALUES"
        ]
    })


    def __init__(self, *, hyperparams: Hyperparams, random_seed: int = 0, docker_containers: typing.Dict[str, str] = None) -> None:
        super().__init__(hyperparams=hyperparams, random_seed=random_seed, docker_containers=docker_containers)
        self._index = None
        self._training_inputs = None
        self._training_outputs = None
        self._fitted = False

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        self._training_inputs = inputs
        self._training_outputs = outputs
        self._fitted = False


    def fit(self, *, timeout: float = None, iterations: int = None) -> None:
        #if self._fitted:
        #    return CallResult(None)

        if self._training_inputs.any() == None or self._training_outputs.any() == None: 
            raise ValueError('Missing training data, or missing values exist.')

        scipy.io.savemat('rpi_data.mat', mdict={'traindata': self._training_inputs, 'trainlabel': self._training_outputs})

        a = rpi_feature_selection_toolbox.initialize()
        index = np.reshape(np.array(a.JMIp()), [-1, ])

        self._index = (index - 1).astype(int)
        self._fitted = True

        os.remove('rpi_data.mat')

        return CallResult(None)


    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> Outputs:  # inputs: m x n numpy array
        if self._fitted:
            return CallResult(inputs[:, self._index])
        else:
            raise ValueError('Model should be fitted first.')


    def get_params(self) -> None:
        pass


    def set_params(self) -> None:
        pass
