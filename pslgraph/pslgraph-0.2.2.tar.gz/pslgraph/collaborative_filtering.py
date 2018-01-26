import logging
import os
import typing

import d3m_metadata.container
import d3m_metadata.hyperparams
import d3m_metadata.metadata
import d3m_metadata.utils
import primitive_interfaces.base
import primitive_interfaces.transformer

from . import config
from .constants import *
from .networkx import Graph, DiGraph
from .util import computeNodeLabel, get_logger, set_logging_level

# TODO(eriq): Pull from dataset meta.
USER_INDEX = 1
ITEM_INDEX = 2
RATING_INDEX = 3

DEBUG_FAST_SIZE = 1000

Inputs = d3m_metadata.container.Dataset
Outputs = d3m_metadata.container.List[Graph]

class CollaborativeFilteringParserHyperparams(d3m_metadata.hyperparams.Hyperparams):
    """
    No hyperparams.
    """

    pass

class CollaborativeFilteringParser(primitive_interfaces.transformer.TransformerPrimitiveBase[Inputs, Outputs, CollaborativeFilteringParserHyperparams]):
    """
    A primitive that transforms collaborative filtering problems into a series of graphs.
    """

    def __init__(self, *, _debug_options: typing.Dict = {}, hyperparams: CollaborativeFilteringParserHyperparams, random_seed: int = 0, docker_containers: typing.Dict[str, str] = None) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed, docker_containers = docker_containers)

        self._logger = get_logger(__name__)
        self._debug_run_fast = False

        if (DEBUG_OPTION_RUN_FAST in _debug_options):
            self._debug_run_fast = _debug_options[DEBUG_OPTION_RUN_FAST]

        if (DEBUG_OPTION_LOGGING_LEVEL in _debug_options):
            set_logging_level(_debug_options[DEBUG_OPTION_LOGGING_LEVEL])

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> primitive_interfaces.base.CallResult[Outputs]:
        self._logger.debug("Starting produce")

        ratings = self._validate_inputs(inputs)
        result = self._process_data(ratings)

        outputs: d3m_metadata.container.List[Graph] = d3m_metadata.container.List[Graph](result)

        metaInfo = {
            'schema': d3m_metadata.metadata.CONTAINER_SCHEMA_VERSION,
            'structural_type': type(outputs),
            'dimension': {
                'length': len(outputs)
            }
        }
        metadata = inputs.metadata.clear(metaInfo, for_value = outputs, source = self)
        metadata = metadata.update((d3m_metadata.metadata.ALL_ELEMENTS,), {'structural_type': Graph}, source = self)
        outputs.metadata = metadata

        return primitive_interfaces.base.CallResult(outputs)

    def _validate_inputs(self, inputs: Inputs):
        if (len(inputs) != 1):
            raise ValueError("Dataset does not have one element. Found %s." % (len(inputs)))

        # TODO(eriq): Fetch this key from metadata.
        ratings = inputs['0']

        for i in range(len(ratings)):
            row = ratings[i]

            if (len(row) != 4):
                raise ValueError("Row {} does not have four columns.", (i))

            row[1] = int(row[1])
            row[2] = int(row[2])
            row[3] = float(row[3])

            if (row[3] < -10.0 or row[3] > 10.0):
                raise ValueError("Row {} is out of range, found: ({}).", (i, row[3]))

        return ratings

    def _process_data(self, ratings):
        self._logger.debug("Processing data")

        user_graph = self._build_source_graph(ratings, USER_INDEX, NODE_MODIFIER_SOURCE)
        item_graph = self._build_source_graph(ratings, ITEM_INDEX, NODE_MODIFIER_TARGET)
        rating_graph = self._build_target_graph(ratings)

        # Add in some hints 

        # We know that it makes sense to compute the mean link prior
        rating_graph.metadata = rating_graph.metadata.update([], {
            'schema': d3m_metadata.metadata.CONTAINER_SCHEMA_VERSION,
            'structural_type': Graph,
            'hints': {
                GRAPH_HINT_LINK_MEAN: True
            }
        })

        # We know that computing the cosine similarity for edges make sense.
        metadata = {
            'schema': d3m_metadata.metadata.CONTAINER_SCHEMA_VERSION,
            'structural_type': Graph,
            'hints': {
                GRAPH_HINT_EDGE_COSINE: True
            }
        }

        user_graph.metadata = user_graph.metadata.update([], metadata)
        item_graph.metadata = item_graph.metadata.update([], metadata)

        return [user_graph, item_graph, rating_graph]

    def _build_source_graph(self, ratings, index, node_modifier):
        graph = Graph()
        elements = set()

        count = 0
        for row in ratings:
            elements.add(row[index])

            count += 1
            if (self._debug_run_fast and count == DEBUG_FAST_SIZE):
                break

        for element in elements:
            label = computeNodeLabel(element, node_modifier)

            attributes = {
                SOURCE_GRAPH_KEY: node_modifier,
                NODE_ID_LABEL: element
            }
            graph.add_node(label, **attributes)

        return graph

    def _build_target_graph(self, ratings):
        graph = DiGraph()

        count = 0
        for row in ratings:
            source_label = computeNodeLabel(row[USER_INDEX], NODE_MODIFIER_SOURCE)
            attributes = {
                SOURCE_GRAPH_KEY: NODE_MODIFIER_SOURCE,
                NODE_ID_LABEL: row[USER_INDEX]
            }
            graph.add_node(source_label, **attributes)

            target_label = computeNodeLabel(row[ITEM_INDEX], NODE_MODIFIER_TARGET)
            attributes = {
                SOURCE_GRAPH_KEY: NODE_MODIFIER_TARGET,
                NODE_ID_LABEL: row[ITEM_INDEX]
            }
            graph.add_node(target_label, **attributes)

            # Normalize the ratings from [-10, 10] to [0, 1]
            # TODO(eriq): How do we discover the range?
            rating = (row[RATING_INDEX] + 10.0) / 20.0

            graph.add_edge(source_label, target_label, weight = rating)

            count += 1
            if (self._debug_run_fast and count == DEBUG_FAST_SIZE):
                break

        return graph

    # TODO(eriq): We should implement a can_accept() that checks the dataset type.

    metadata = d3m_metadata.metadata.PrimitiveMetadata({
        # Required
        'id': 'fdc99781-08d0-4cc0-b41a-2d17adcfaa1e',
        'version': config.VERSION,
        'name': 'Collaborative Filtering Parser',
        'description': 'Transform "collaborative filtering"-like problems into pure graphs.',
        'python_path': 'd3m.primitives.pslgraph.CollaborativeFilteringParser',
        'primitive_family': d3m_metadata.metadata.PrimitiveFamily.DATA_TRANSFORMATION,
        'algorithm_types': [
            d3m_metadata.metadata.PrimitiveAlgorithmType.COMPUTER_ALGEBRA,
        ],
        'source': {
            'name': config.D3M_PERFORMER_TEAM,
            'uris': [ config.REPOSITORY ]
        },

        # Optional
        'keywords': [ 'preprocessing', 'primitive', 'graph', 'dataset', 'transformer'],
        'installation': [ config.INSTALLATION ],
        'location_uris': [],
        'precondition': [ d3m_metadata.metadata.PrimitiveEffects.NO_MISSING_VALUES ],
        'effects': [ d3m_metadata.metadata.PrimitiveEffects.NO_MISSING_VALUES ],
        'hyperparms_to_tune': []
    })
