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

from .graph_matching import GraphMatchingParser, GraphMatchingParserHyperparams
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

# TODO(eriq): Hyperparam?
TRUTH_THRESHOLD = 0.5

class Hyperparams(d3m_metadata.hyperparams.Hyperparams):
    """
    No hyperparams.
    """

    pass

class Params(d3m_metadata.params.Params):
    pass

class GraphMatchingLinkPrediction(primitive_interfaces.supervised_learning.SupervisedLearnerPrimitiveBase[Inputs, Outputs, Params, Hyperparams]):
    """
    A primitive that takes a graph matching problem and does full link prediction on it.
    This just strings together various other primitives.
    """

    def __init__(self, *, hyperparams: Hyperparams, random_seed: int = 0, _debug_options: typing.Dict = {}, docker_containers: typing.Dict[str, str] = None) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed, docker_containers = docker_containers)

        self._gm_parser = GraphMatchingParser(hyperparams = GraphMatchingParserHyperparams(), _debug_options = _debug_options)
        self._transformer = GraphTransformer(hyperparams = GraphTransformerHyperparams(), _debug_options = _debug_options)
        self._link_prediction = LinkPrediction(hyperparams = LinkPredictionHyperparams(), _debug_options = _debug_options)

        self._training_dataset = None

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
        input_graph = self._full_transform(self._training_dataset, inputs)
        # Normally, we would use the training graph for weight learning and this one for inference.
        # However, the data is split incorrectly.
        # So instead, we will run inference on the training graph and just grab the desired edges from the test dataset.
        output_graph = self._link_prediction.produce(inputs = input_graph, timeout = timeout, iterations = iterations).value[0]

        outputs: d3m_metadata.container.DataFrame = self._get_target_links(inputs, output_graph)

        return primitive_interfaces.base.CallResult(outputs)

    # TODO(eriq): Do we have any params?
    def get_params(self) -> Params:
        return Params({})

    def set_params(self, *, params: Params) -> None:
        pass

    # Take in a dataset and turn it into a graph for link prediction.
    def _full_transform(self, dataset: Inputs, test_dataset: Inputs) -> d3m_metadata.container.List[Graph]:
        parsed_graphs = self._gm_parser.produce(inputs = dataset).value

        # Because the test data is split incorrectly,
        # we have to merge the train and test data together.
        link_graph = parsed_graphs[2]
        for row in test_dataset[GRAPH_MATCHING_DATASET_TABLE_INDEX]:
            source_node_id = row[1]
            target_node_id = row[2]

            source_label = computeNodeLabel(source_node_id, NODE_MODIFIER_SOURCE)
            target_label = computeNodeLabel(target_node_id, NODE_MODIFIER_TARGET)

            if (not link_graph.has_node(source_label)):
                attributes = {
                    SOURCE_GRAPH_KEY: NODE_MODIFIER_SOURCE,
                    NODE_ID_LABEL: source_node_id,
                }
                link_graph.add_node(source_label, **attributes)

            if (not link_graph.has_node(target_label)):
                attributes = {
                    SOURCE_GRAPH_KEY: NODE_MODIFIER_TARGET,
                    NODE_ID_LABEL: target_node_id,
                }
                link_graph.add_node(target_label, **attributes)

            if (not link_graph.has_edge(source_label, target_label)):
                attributes = {
                    WEIGHT_KEY: -1,
                    TARGET_KEY: True
                }
                link_graph.add_edge(source_label, target_label, **attributes)

        return self._transformer.produce(inputs = parsed_graphs).value

    # Use the input dataset and output graph to get the values for the desired links.
    def _get_target_links(self, dataset: Inputs, output_graph: Graph) -> d3m_metadata.container.DataFrame:
        d3m_indexes = []
        matches = []

        true_links = self._get_true_links(output_graph)

        for row in dataset[GRAPH_MATCHING_DATASET_TABLE_INDEX]:
            d3m_index = row[0]
            source_node_id = row[1]
            target_node_id = row[2]

            source_label = computeNodeLabel(source_node_id, NODE_MODIFIER_SOURCE)
            target_label = computeNodeLabel(target_node_id, NODE_MODIFIER_TARGET)

            d3m_indexes.append(d3m_index)
            if ((source_label, target_label) in true_links):
                matches.append(1)
            else:
                matches.append(0)

        return pandas.DataFrame(data = {'d3mIndex': d3m_indexes, 'match': matches})

    # Returns: {(source label, target label): True, ...}
    def _get_true_links(self, graph: Graph) -> typing.Dict:
        links = {}

        for (source, target, data) in graph.edges(data = True):
            # Skip edges.
            if (data[EDGE_TYPE_KEY] != EDGE_TYPE_LINK):
                continue

            if (data[WEIGHT_KEY] >= TRUTH_THRESHOLD):
                links[(source, target)] = True

        return links

    # Returns: {source label: (best target label, best target value), ...}.
    def _get_best_links(self, graph: Graph) -> typing.Dict:
        links = {}

        for (source, target, data) in graph.edges(data = True):
            # Skip edges.
            if (data[EDGE_TYPE_KEY] != EDGE_TYPE_LINK):
                continue

            if (source not in links or links[source][1] < data[WEIGHT_KEY]):
                links[source] = (target, data[WEIGHT_KEY])

        return links

    # TODO(eriq): We should implement a can_accept() that ensures we only have a graph-matching problem dataset.

    metadata = d3m_metadata.metadata.PrimitiveMetadata({
        # Required
        'id': '2d782d55-f7ac-4abe-b228-39afcda1bbb3',
        'version': config.VERSION,
        'name': 'Graph Matching Link Prediction',
        'description': 'Give a full solution to "graph matching"-like problems using collective link prediction.',
        'python_path': 'd3m.primitives.pslgraph.GraphMatchingLinkPrediction',
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
