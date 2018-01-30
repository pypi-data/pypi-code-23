import os
import typing

import d3m_metadata.container
import d3m_metadata.hyperparams
import d3m_metadata.metadata
import d3m_metadata.params
import d3m_metadata.utils
import pandas
import primitive_interfaces.base
import primitive_interfaces.supervised_learning
import primitive_interfaces.transformer

from .collaborative_filtering import CollaborativeFilteringParser, CollaborativeFilteringParserHyperparams
from .graph_transform import GraphTransformerHyperparams, GraphTransformer
from .link_prediction import LinkPrediction, LinkPredictionHyperparams, LinkPredictionParams

from . import config
from .constants import *
from .networkx import Graph, DiGraph
from .util import computeNodeLabel

# The test data will just look like a dataset, but the match column will be empty.
Inputs = d3m_metadata.container.Dataset
# Return match or no match.
Outputs = d3m_metadata.container.DataFrame

class CollaborativeFilteringLinkPredictionHyperparams(d3m_metadata.hyperparams.Hyperparams):
    scale_rating = d3m_metadata.hyperparams.Hyperparameter[bool](
            default = True,
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'])

    collaborative_filtering_parser_hyperparams = d3m_metadata.hyperparams.Hyperparameter(
            default = CollaborativeFilteringParserHyperparams.defaults(),
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'])

    graph_transform_hyperparams = d3m_metadata.hyperparams.Hyperparameter(
            default = GraphTransformerHyperparams.defaults(),
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'])

    link_prediction_hyperparams = d3m_metadata.hyperparams.Hyperparameter(
            default = LinkPredictionHyperparams.defaults(),
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'])

# TODO(eriq): LinkPrediction currently doesn't carry any state, but it will some day.
class CollaborativeFilteringLinkPredictionParams(d3m_metadata.params.Params):
    training_set: Inputs
    debug_options: typing.Dict

class CollaborativeFilteringLinkPrediction(primitive_interfaces.supervised_learning.SupervisedLearnerPrimitiveBase[Inputs, Outputs, CollaborativeFilteringLinkPredictionParams, CollaborativeFilteringLinkPredictionHyperparams]):
    """
    A primitive that takes a collaborative filtering problem and does full link prediction on it.
    This just strings together various other primitives.
    """

    def __init__(self, *, hyperparams: CollaborativeFilteringLinkPredictionHyperparams, random_seed: int = 0, _debug_options: typing.Dict = {}, docker_containers: typing.Dict[str, str] = None) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed, docker_containers = docker_containers)

        self._cf_parser = CollaborativeFilteringParser(
                hyperparams = self.hyperparams['collaborative_filtering_parser_hyperparams'],
                _debug_options = _debug_options)

        self._transformer = GraphTransformer(
                hyperparams = self.hyperparams['graph_transform_hyperparams'],
                _debug_options = _debug_options)

        self._link_prediction = LinkPrediction(
                hyperparams = self.hyperparams['link_prediction_hyperparams'],
                _debug_options = _debug_options)

        self._training_dataset = None
        self._set_debug_options(_debug_options)

    def _set_debug_options(self, _debug_options):
        self._debug_options = _debug_options

        self._cf_parser._set_debug_options(_debug_options)
        self._transformer._set_debug_options(_debug_options)
        self._link_prediction._set_debug_options(_debug_options)

    # TODO(eriq): We get the output labels from the dataset itself, why is it here as well?
    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        self._training_dataset = inputs

        # See produce() about this.
        # self._link_prediction.set_training_data(inputs = self._full_transform(inputs), outputs = None)

    def fit(self, *, timeout: float = None, iterations: int = None) -> primitive_interfaces.base.CallResult[None]:
        # See produce() about this.
        # return self._link_prediction.fit(timeout = timeout, iterations = iterations)
        return primitive_interfaces.base.CallResult(None)

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> primitive_interfaces.base.CallResult[Outputs]:
        # Normally, we would use the training graph for weight learning and this one for inference.
        # However, the data is split incorrectly.
        # The test data is just a holdout of the training data, so the graph is the same.
        parsed_graphs = self._cf_parser.produce(inputs = self._training_dataset).value
        input_graph = self._transformer.produce(inputs = parsed_graphs).value

        output_graph = self._link_prediction.produce(inputs = input_graph, timeout = timeout, iterations = iterations).value[0]

        outputs: d3m_metadata.container.DataFrame = self._get_target_links(inputs, output_graph)

        return primitive_interfaces.base.CallResult(outputs)

    def get_params(self) -> CollaborativeFilteringLinkPredictionParams:
        return CollaborativeFilteringLinkPredictionParams({
            'training_set': self._training_dataset,
            'debug_options': self._debug_options
        })

    def set_params(self, *, params: CollaborativeFilteringLinkPredictionParams) -> None:
        self._training_dataset = params['training_set']
        self._set_debug_options(params['debug_options'])

    # Use the input dataset and output graph to get the values for the desired links.
    def _get_target_links(self, dataset: Inputs, output_graph: Graph) -> d3m_metadata.container.DataFrame:
        d3m_indexes = []
        ratings = []

        min_rating = self.hyperparams['collaborative_filtering_parser_hyperparams']['min_rating']
        max_rating = self.hyperparams['collaborative_filtering_parser_hyperparams']['max_rating']

        # TODO(eriq): Fetch this key from metadata.
        for row in dataset['0']:
            d3m_index = row[0]
            source_node_id = row[1]
            target_node_id = row[2]

            source_label = computeNodeLabel(source_node_id, NODE_MODIFIER_SOURCE)
            target_label = computeNodeLabel(target_node_id, NODE_MODIFIER_TARGET)

            d3m_indexes.append(d3m_index)
            if (not output_graph.has_edge(source_label, target_label)):
                ratings.append(0)
            else:
                weight = output_graph[source_label][target_label][WEIGHT_KEY]

                # Scale the results back to the input domain.
                if (self.hyperparams['scale_rating']):
                    weight = weight * (max_rating - min_rating) + min_rating

                ratings.append(weight)

        return pandas.DataFrame(data = {'d3mIndex': d3m_indexes, 'rating': ratings})

    # TODO(eriq): We should implement a can_accept() that ensures we only have a graph-matching problem dataset.

    metadata = d3m_metadata.metadata.PrimitiveMetadata({
        # Required
        'id': 'f9440843-5791-4d58-b0a8-617b5cb2371d',
        'version': config.VERSION,
        'name': 'Collaborative Filtering Link Prediction',
        'description': 'Give a full solution to "collaborative filtering"-like problems using collective link prediction.',
        'python_path': 'd3m.primitives.pslgraph.CollaborativeFilteringLinkPrediction',
        'primitive_family': d3m_metadata.metadata.PrimitiveFamily.LINK_PREDICTION,
        'algorithm_types': [
            d3m_metadata.metadata.PrimitiveAlgorithmType.MARKOV_LOGIC_NETWORK,
        ],
        'source': {
            'name': config.D3M_PERFORMER_TEAM,
            'uris': [ config.REPOSITORY ]
        },

        # Optional
        'keywords': [ 'preprocessing', 'primitive', 'graph', 'dataset', 'transformer', 'link prediction', 'collective classifiction'],
        'installation': [ config.INSTALLATION ],
        'location_uris': [],
        'precondition': [ d3m_metadata.metadata.PrimitiveEffects.NO_MISSING_VALUES ],
        'effects': [ d3m_metadata.metadata.PrimitiveEffects.NO_MISSING_VALUES ],
        'hyperparms_to_tune': []
    })
