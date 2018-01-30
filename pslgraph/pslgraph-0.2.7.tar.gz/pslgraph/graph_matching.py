import logging
import os
import typing

import networkx # type: ignore

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

Inputs = d3m_metadata.container.Dataset
Outputs = d3m_metadata.container.List[Graph]

class GraphMatchingParserHyperparams(d3m_metadata.hyperparams.Hyperparams):
    pass

class GraphMatchingParser(primitive_interfaces.transformer.TransformerPrimitiveBase[Inputs, Outputs, GraphMatchingParserHyperparams]):
    """
    A primitive that transforms graph matching problems with multiple graphs into a single graph for later processing.
    """

    def __init__(self, *, _debug_options: typing.Dict = {}, hyperparams: GraphMatchingParserHyperparams, random_seed: int = 0, docker_containers: typing.Dict[str, str] = None) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed, docker_containers = docker_containers)

        self._logger = get_logger(__name__)

        self._set_debug_options(_debug_options)

    def _set_debug_options(self, _debug_options):
        if (DEBUG_OPTION_LOGGING_LEVEL in _debug_options):
            set_logging_level(_debug_options[DEBUG_OPTION_LOGGING_LEVEL])

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> primitive_interfaces.base.CallResult[Outputs]:
        self._logger.debug("Starting produce")

        graph1, graph2, observedLinks = self._validate_inputs(inputs)
        result = self._process_data(graph1, graph2, observedLinks)

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
        if (len(inputs) != 3):
            raise ValueError("Dataset does not have three elements. Found %s." % (len(inputs)))

        # TODO(eriq): Fetch these keys from metadata.
        graph1 = inputs['0']
        graph2 = inputs['1']
        observedLinks = inputs['2']

        if (not isinstance(graph1, networkx.Graph)):
            raise ValueError("Expecting a graph at \"'0'\", found a %s" % (type(graph1).__name__))

        if (not isinstance(graph2, networkx.Graph)):
            raise ValueError("Expecting a graph at \"'1'\", found a %s" % (type(graph2).__name__))

        for i in range(len(observedLinks)):
            row = observedLinks[i]

            if (len(row) != 4):
                raise ValueError("Row {} in the tabular data that does not have four columns.", (i))

            row[1] = int(row[1])
            row[2] = int(row[2])

            if (row[3] != '0' and row[3] != '1' and row[3] != ''):
                raise ValueError("Row {} in the tabular data that does end with 0/1 or empty string, found: ({}).", (i, row[3]))

            if (row[3] == ''):
                row[3] = None
            else:
                row[3] = float(row[3])
                if (row[3] < 0.0 or row[3] > 1.0):
                    raise ValueError("Row {} in the tabular data has a weight that is out of range [0, 1]: ({}).", i, row[3])

        return Graph(graph1), Graph(graph2), observedLinks

    # Return a new graph with properly labeled nodes.
    def _relabel(self, input_graph, node_modifier):
        output_graph = Graph()

        # First add all the nodes.
        for (id, data) in input_graph.nodes(data = True):
            label = computeNodeLabel(data[NODE_ID_LABEL], node_modifier)

            data[SOURCE_GRAPH_KEY] = node_modifier
            data[NODE_ID_LABEL] = data[NODE_ID_LABEL]

            output_graph.add_node(label, **data)

        # Now add all the edges.
        for (source, target, data) in input_graph.edges(data = True):
            source_id = input_graph.node[source][NODE_ID_LABEL]
            target_id = input_graph.node[target][NODE_ID_LABEL]

            # Disallow self edges.
            if (source == target or source_id == target_id):
                continue

            weight = 1.0
            if (WEIGHT_KEY in data):
                weight = data[WEIGHT_KEY]

            # Remember, these edges are within the same input graph.
            source_label = computeNodeLabel(source_id, node_modifier)
            target_label = computeNodeLabel(target_id, node_modifier)

            data[WEIGHT_KEY] = weight
            data[EDGE_TYPE_KEY] = EDGE_TYPE_EDGE
            data[OBSERVED_KEY] = True

            output_graph.add_edge(source_label, target_label, **data)

        return output_graph

    def _process_data(self, graph1, graph2, observedLinks):
        self._logger.debug("Processing data")

        graph1 = self._relabel(graph1, NODE_MODIFIER_SOURCE)
        graph2 = self._relabel(graph2, NODE_MODIFIER_TARGET)

        # Build up the graph of observed links.
        observedGraph = DiGraph()
        for row in observedLinks:
            # If there is no weight, then this is test data,
            # Skip this link.
            # TODO(eriq): Think about this more.
            if (row[3] == None):
                continue

            source = int(row[1])
            target = int(row[2])
            weight = float(row[3])

            sourceLabel = computeNodeLabel(source, NODE_MODIFIER_SOURCE)
            targetLabel = computeNodeLabel(target, NODE_MODIFIER_TARGET)

            attributes = {
                SOURCE_GRAPH_KEY: NODE_MODIFIER_SOURCE,
                NODE_ID_LABEL: source,
            }
            observedGraph.add_node(sourceLabel, **attributes)

            attributes = {
                SOURCE_GRAPH_KEY: NODE_MODIFIER_TARGET,
                NODE_ID_LABEL: target,
            }
            observedGraph.add_node(targetLabel, **attributes)

            observedGraph.add_edge(sourceLabel, targetLabel, weight = weight)

        # Add in some hints 
        # We know that it makes sense to compute the local feature based similarity of the links.
        for graph in [graph1, graph2, observedGraph]:
            graph.metadata = graph.metadata.update([], {
                'schema': d3m_metadata.metadata.CONTAINER_SCHEMA_VERSION,
                'structural_type': Graph,
                'hints': {
                    GRAPH_HINT_LINK_LOCAL_SIM: True
                }
            })

        return [graph1, graph2, observedGraph]

    # TODO(eriq): We should implement a can_accept() that ensures we only have a graph-matching problem dataset.

    metadata = d3m_metadata.metadata.PrimitiveMetadata({
        # Required
        'id': '3c4a1c2a-0f88-4fb1-a1b5-23226a38741b',
        'version': config.VERSION,
        'name': 'Graph Matching Parser',
        'description': 'Transform "graph matching"-like problems into pure graphs.',
        'python_path': 'd3m.primitives.pslgraph.GraphMatchingParser',
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
