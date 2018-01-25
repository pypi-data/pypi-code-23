import logging
import operator
import os
import re
import typing

import d3m_metadata.container
import d3m_metadata.hyperparams
import d3m_metadata.metadata
import d3m_metadata.params
import d3m_metadata.utils
import primitive_interfaces.base
import primitive_interfaces.supervised_learning

from .constants import *
from .networkx import Graph, DiGraph
from .util import computeNodeLabel, get_logger, set_logging_level
from .psl import buildOutputGraph, runModel, writePSLData

# TODO(eriq): Use the training data for weight learning?

# We can take just the annotated graph.
# TODO(eriq): How do we fix the size?
Inputs = d3m_metadata.container.List[Graph]
Outputs = d3m_metadata.container.List[Graph]

# TODO(eriq): Include all edges in targets? (param)

PSL_MODEL = 'link_prediction'

class LinkPredictionHyperparams(d3m_metadata.hyperparams.Hyperparams):
    pass

class LinkPredictionParams(d3m_metadata.params.Params):
    pass

class LinkPrediction(primitive_interfaces.supervised_learning.SupervisedLearnerPrimitiveBase[Inputs, Outputs, LinkPredictionParams, LinkPredictionHyperparams]):
    """
    A primitive that performs link prediction on an annotated graph.
    """

    def __init__(self, *, hyperparams: LinkPredictionHyperparams, random_seed: int = 0, _debug_options: typing.Dict = {}, docker_containers: typing.Dict[str, str] = None) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed, docker_containers = docker_containers)

        self._logger = get_logger(__name__)

        if (DEBUG_OPTION_LOGGING_LEVEL in _debug_options):
            set_logging_level(_debug_options[DEBUG_OPTION_LOGGING_LEVEL])

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> primitive_interfaces.base.CallResult[Outputs]:
        self._logger.debug("Starting produce")

        annotatedGraph = self._validateInputs(inputs)
        result = self._linkPrediction(annotatedGraph)

        outputs: d3m_metadata.container.List[Graph] = d3m_metadata.container.List[Graph]([result])
        metaInfo = {
            'schema': d3m_metadata.metadata.CONTAINER_SCHEMA_VERSION,
            'structural_type': type(outputs),
            'dimension': {
                'length': len(outputs)
            }
        }
        metadata = inputs.metadata.clear(metaInfo, for_value = outputs, source=self)
        metadata = metadata.update((d3m_metadata.metadata.ALL_ELEMENTS,), {'structural_type': int}, source = self)
        outputs.metadata = metadata

        return primitive_interfaces.base.CallResult(outputs)

    def _linkPrediction(self, graph):
        writePSLData(graph)
        pslOutput = runModel(PSL_MODEL)
        return buildOutputGraph(pslOutput[LINK_PREDICATE], graph)

    def _validateInputs(self, inputs: Inputs):
        if (len(inputs) != 1):
            raise ValueError("Not exactly one input, found %d." % (len(inputs)))

        graph = inputs[0]

        if (not isinstance(graph, Graph)):
            raise ValueError("Expecting a graph, found a %s" % (type(graph).__name__))

        return graph

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        # Weight learning not yet supported.
        pass

    def fit(self, *, timeout: float = None, iterations: int = None) -> primitive_interfaces.base.CallResult[None]:
        # Weight learning not yet supported.
        return primitive_interfaces.base.CallResult(None)

    # TODO(eriq): Do we have any params?
    def get_params(self) -> LinkPredictionParams:
        return LinkPredictionParams({})

    def set_params(self, *, params: LinkPredictionParams) -> None:
        pass

    # TODO(eriq): We should implement a can_accept() that ensures we only have a graph-matching problem dataset.

    metadata = d3m_metadata.metadata.PrimitiveMetadata({
        'id': 'd83aa8fe-0433-4462-be54-b4074959b6fc',
        'version': '0.0.1',
        'name': "PSL Link Prediction",
        'keywords': ['primitive', 'graph', 'link prediction', 'PSL'],
        'source': {
            'name': 'SRI/UCSC Team',
            'uris': [
                # TODO(eriq)
                # Unstructured URIs. Link to file and link to repo in this case.
                # 'https://gitlab.com/datadrivendiscovery/tests-data/blob/master/primitives/test_primitives/increment.py',
                # 'https://gitlab.com/datadrivendiscovery/tests-data.git',
            ],
        },
        # TODO(eriq)
        'installation': [{
            'type': d3m_metadata.metadata.PrimitiveInstallationType.PIP,
            'package_uri': 'git+https://gitlab.com/datadrivendiscovery/tests-data.git@{git_commit}#egg=test_primitives&subdirectory=primitives'.format(
                git_commit=d3m_metadata.utils.current_git_commit(os.path.dirname(__file__)),
            ),
        }],
        # URIs at which one can obtain code for the primitive, if available.
        # TODO(eriq)
        'location_uris': [
            'https://gitlab.com/datadrivendiscovery/tests-data/raw/{git_commit}/primitives/test_primitives/increment.py'.format(
                git_commit=d3m_metadata.utils.current_git_commit(os.path.dirname(__file__)),
            ),
        ],
        # TODO(eriq)
        # The same path the primitive is registered with entry points in setup.py.
        'python_path': 'd3m.primitives.test.IncrementPrimitive',
        'algorithm_types': [
            d3m_metadata.metadata.PrimitiveAlgorithmType.COMPUTER_ALGEBRA,
        ],
        'primitive_family': d3m_metadata.metadata.PrimitiveFamily.DATA_TRANSFORMATION,
        'preconditions': [
            d3m_metadata.metadata.PrimitivePrecondition.NO_MISSING_VALUES,
            d3m_metadata.metadata.PrimitivePrecondition.NO_CATEGORICAL_VALUES,
        ]
    })
