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
import primitive_interfaces.transformer

from .constants import *
from .networkx import Graph, DiGraph
from .util import computeNodeLabel, get_logger, set_logging_level

# TODO(eriq): Change the output to just a graph once there is officially metadata on it.
Inputs = d3m_metadata.container.List[Graph]
Outputs = d3m_metadata.container.List[Graph]

# TODO(eriq): More through explaniation of input and output annotations.
"""
We expect two or three graphs as input:
- A graph describing the source nodes for the downstream link prediction problem.
- A graph describing the target nodes for the downstream link prediction problem.
- An optional graph describing existing links bewteen these two graphs.
The nodes in the source graph will maintain their "nodeID" and will get an additional attribute: SOURCE_GRAPH_KEY
indicating if thise node came from the source graph (NODE_MODIFIER_SOURCE) or target graph (NODE_MODIFIER_TARGET).
The label for these nodes will additionally become: (nodeID + 1) * SOURCE_GRAPH_KEY.
This is because nodeIDs can overlap between graphs.
The +1 is because zero is a valid nodeID, but they are non-negative.
"""

DEBUG_OPTION_RUN_FAST = 'run_fast'

DEFAULT_FEATURE_PATTERN = r'f\d+'
# DEFAULT_MAX_LINKS_PER_NODE = 50
DEFAULT_MAX_LINKS_PER_NODE = 10
DEFAULT_MAX_COMPUTED_EDGES = 500

class GraphTransformerHyperparams(d3m_metadata.hyperparams.Hyperparams):
    """
    No hyperparams.
    """

    pass

class GraphTransformer(primitive_interfaces.transformer.TransformerPrimitiveBase[Inputs, Outputs, GraphTransformerHyperparams]):
    """
    A primitive that transforms multiple graphs into a single annotated graph that can be consumed by PSL.
    """

    def __init__(self, *, hyperparams: GraphTransformerHyperparams, _debug_options: typing.Dict = {}, random_seed: int = 0, docker_containers: typing.Dict[str, str] = None) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed, docker_containers = docker_containers)

        self._logger = get_logger(__name__)
        self._debug_run_fast = False

        if (DEBUG_OPTION_RUN_FAST in _debug_options):
            self._debug_run_fast = _debug_options[DEBUG_OPTION_RUN_FAST]

        if (DEBUG_OPTION_LOGGING_LEVEL in _debug_options):
            set_logging_level(_debug_options[DEBUG_OPTION_LOGGING_LEVEL])

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> primitive_interfaces.base.CallResult[Outputs]:
        self._logger.debug("Starting produce")

        input_source_graph, input_target_graph, link_graph = self._validate_inputs(inputs)
        result = self._process_data(input_source_graph, input_target_graph, link_graph)

        outputs: d3m_metadata.container.List[Graph] = d3m_metadata.container.List[Graph]([result])

        metaInfo = {
            'schema': d3m_metadata.metadata.CONTAINER_SCHEMA_VERSION,
            'structural_type': type(outputs),
            'dimension': {
                'length': len(outputs)
            }
        }
        metadata = inputs.metadata.clear(metaInfo, for_value = outputs, source=self)
        metadata = metadata.update((d3m_metadata.metadata.ALL_ELEMENTS,), {'structural_type': Graph}, source = self)
        outputs.metadata = metadata

        return primitive_interfaces.base.CallResult(outputs)

    def _validate_inputs(self, inputs: Inputs):
        if (len(inputs) < 2):
            raise ValueError("Not enough values for input. Need at least 2, found %d." % (len(inputs)))

        if (len(inputs) > 3):
            raise ValueError("Too many values for input. Need at most 3, found %d." % (len(inputs)))

        # TODO(eriq): Fetch these keys from metadata.
        input_source_graph = inputs[0]
        input_target_graph = inputs[1]

        link_graph = None
        if (len(inputs) == 3):
            link_graph = inputs[2]

        if (not isinstance(input_source_graph, Graph)):
            raise ValueError("Expecting a graph at \"'0'\", found a %s" % (type(input_source_graph).__name__))

        if (not isinstance(input_target_graph, Graph)):
            raise ValueError("Expecting a graph at \"'1'\", found a %s" % (type(input_target_graph).__name__))

        if (link_graph is not None and not isinstance(link_graph, DiGraph)):
            raise ValueError("Expecting a directed graph at \"'2'\", found a %s" % (type(link_graph).__name__))

        return input_source_graph, input_target_graph, link_graph

    def _process_data(self, input_source_graph, input_target_graph, link_graph):
        self._logger.debug("Processing data")

        output_graph = Graph()

        hints = self._check_hints(input_source_graph, input_target_graph, link_graph)

        self._process_graph(output_graph, input_source_graph, NODE_MODIFIER_SOURCE)
        self._process_graph(output_graph, input_target_graph, NODE_MODIFIER_TARGET)

        explicit_targets = []
        if (link_graph is not None):
            explicit_targets = self._process_links(output_graph, link_graph)

        if (hints[GRAPH_HINT_LINK_LOCAL_SIM]):
            self._compute_local_sim_link_weights(output_graph, input_source_graph, input_target_graph, explicit_targets)

        # TODO(eriq): Other Computations

        # Ensure that explicit targets are included.
        self._logger.debug("Adding explicit targets (%d).", len(explicit_targets))
        for (source_node_id, target_node_id) in explicit_targets:
            source_label = computeNodeLabel(source_node_id, NODE_MODIFIER_SOURCE)
            target_label = computeNodeLabel(target_node_id, NODE_MODIFIER_TARGET)

            if (output_graph.has_edge(source_label, target_label)):
                continue

            attributes = {
                EDGE_TYPE_KEY: EDGE_TYPE_LINK,
                TARGET_KEY: True,
                OBSERVED_KEY: False
            }
            output_graph.add_edge(source_label, target_label, **attributes)
            
        # Attached the used hints as metadata in the output graph.
        output_graph.metadata = output_graph.metadata.update([], {
            'schema': d3m_metadata.metadata.CONTAINER_SCHEMA_VERSION,
            'structural_type': Graph,
            'hints': hints
        })

        return output_graph

    # Add the nodes and edges from a single graph.
    def _process_graph(self, output_graph, input_graph, nodeModifier):
        # First add all the nodes.
        for nodeId in input_graph.nodes():
            label = computeNodeLabel(input_graph.node[nodeId][NODE_ID_LABEL], nodeModifier)
            attributes = {
                SOURCE_GRAPH_KEY: nodeModifier,
                NODE_ID_LABEL: input_graph.node[nodeId][NODE_ID_LABEL],
            }
            output_graph.add_node(label, **attributes)

        # Now add all the edges.
        for (source, target) in input_graph.edges():
            source_id = input_graph.node[source][NODE_ID_LABEL]
            target_id = input_graph.node[target][NODE_ID_LABEL]

            # Disallow self edges.
            if (source == target or source_id == target_id):
                continue

            weight = 1.0
            if (WEIGHT_KEY in input_graph[source][target]):
                weight = input_graph[source][target][WEIGHT_KEY]

            # Remember, these edges are within the same input graph.
            source_label = computeNodeLabel(source_id, nodeModifier)
            target_label = computeNodeLabel(target_id, nodeModifier)

            attributes = {
                WEIGHT_KEY: weight,
                EDGE_TYPE_KEY: EDGE_TYPE_EDGE,
                OBSERVED_KEY: True
            }
            output_graph.add_edge(source_label, target_label, **attributes)

    # Add observed links and check for explicit targets.
    def _process_links(self, output_graph, link_graph):
        targets = []

        # All the nodes should already exist in each respective graph.
        for (source, target, data) in link_graph.edges(data = True):
            source_node_id = link_graph.node[source][NODE_ID_LABEL]
            target_node_id = link_graph.node[target][NODE_ID_LABEL]

            source_label = computeNodeLabel(source_node_id, NODE_MODIFIER_SOURCE)
            target_label = computeNodeLabel(target_node_id, NODE_MODIFIER_TARGET)

            if (TARGET_KEY in data and data[TARGET_KEY]):
                # This link is an explicit target, make sure to include it in targets.
                targets.append((int(source_node_id), int(target_node_id)))
            else:
                # This link is observed.
                weight = 1.0
                if (WEIGHT_KEY in link_graph[source][target]):
                    weight = float(link_graph[source][target][WEIGHT_KEY])

                attributes = {
                    WEIGHT_KEY: weight,
                    EDGE_TYPE_KEY: EDGE_TYPE_LINK,
                    OBSERVED_KEY: True
                }

                output_graph.add_edge(source_label, target_label, **attributes)

        return targets

    # Looks for hints and reconcile them with any additional options.
    # TODO(eriq): Allows params or hyperparams to override hints.
    def _check_hints(self, *graphs):
        hints = {
            GRAPH_HINT_LINK_LOCAL_SIM: False,
            GRAPH_HINT_LINK_MEAN: False,
            # We can get different hints about each input graph.
            GRAPH_HINT_EDGE_COSINE: (False, False),
        }

        # First check for hints from each graph.
        for i in range(len(graphs)):
            graphHints = graphs[i].metadata.query([])['hints']

            if (not graphHints):
                continue

            if (GRAPH_HINT_LINK_LOCAL_SIM in graphHints):
                hints[GRAPH_HINT_LINK_LOCAL_SIM] = graphHints[GRAPH_HINT_LINK_LOCAL_SIM]

            if (GRAPH_HINT_LINK_MEAN in graphHints):
                hints[GRAPH_HINT_LINK_MEAN] = graphHints[GRAPH_HINT_LINK_MEAN]

            if (GRAPH_HINT_EDGE_COSINE in graphHints and i < 2):
                hints[GRAPH_HINT_EDGE_COSINE][i] = graphHints[GRAPH_HINT_EDGE_COSINE]

        return hints

    # Look for node attributes that look like features get the distance (normalized into similarity) between them.
    # TODO(eriq): Make blocking tunable.
    # TODO(eriq): Features from hints
    # TODO(eriq): Where are some target links that we want to make sure are included.
    def _compute_local_sim_link_weights(self, output_graph, input_source_graph, input_target_graph, explicit_targets):
        self._logger.debug("Computing local link similarity")

        features = self._discoverFeatures(input_source_graph, input_target_graph)

        # {id1: {id2: [distance, ...], ...}, ...}
        # id1 < id2
        distances = {}

        for feature in features:
            minVal = None
            maxVal = None

            for id1 in input_source_graph.nodes():
                source_label = computeNodeLabel(input_source_graph.node[id1][NODE_ID_LABEL], NODE_MODIFIER_SOURCE)

                # TEST
                count = 0

                for id2 in input_target_graph.nodes():
                    target_label = computeNodeLabel(input_target_graph.node[id2][NODE_ID_LABEL], NODE_MODIFIER_TARGET)

                    # Only calcualte distance for links not already observed in the output graph.
                    if (output_graph.has_edge(source_label, target_label) and output_graph[source_label][target_label][OBSERVED_KEY]):
                        continue
                    
                    distance = abs(input_source_graph.node[id1][feature] - input_target_graph.node[id2][feature])

                    if (minVal is None or distance < minVal):
                        minVal = distance

                    if (maxVal is None or distance > maxVal):
                        maxVal = distance

                    if (id1 not in distances):
                        distances[id1] = {}

                    if (id2 not in distances[id1]):
                        distances[id1][id2] = []

                    distances[id1][id2].append(distance)

                    # TEST
                    count += 1
                    if self._debug_run_fast and count == int(DEFAULT_MAX_LINKS_PER_NODE / 2):
                        break

            # Just do a min/max normalization into a similarity.
            # TODO(eriq): Better normalization here can go a long way.
            rangeVal = float(maxVal - minVal)
            for (id1, id2Distances) in distances.items():
                for (id2, pairDistances) in id2Distances.items():
                    distance = pairDistances[-1]
                    pairDistances[-1] = (1.0 - min(1.0, max(0.0, float(distance - minVal) / rangeVal)))

        # Just get the mean or the normalized values, but we could also do
        # something like a logistic regression on the raw values.
        # now distances = {id1: {id2: nomral distance, ...}, ...}
        for (id1, id2Sims) in distances.items():
            for (id2, pairSims) in id2Sims.items():
                distances[id1][id2] = float(sum(pairSims)) / len(pairSims)

        # For blocking purposes, choose the top N similarities for each node.
        blockedSims = {}

        ''' TEST(eriq): This is pretty costly (750k in test data). Can we make it cheaper?
        # Before we block, include all information from both sides of explicit targets.
        include_sources = {explicit_target[0] for explicit_target in explicit_targets}
        include_targets = {explicit_target[1] for explicit_target in explicit_targets}
        for (id1, id2Sims) in distances.items():
            node_id_1 = input_source_graph.node[id1][NODE_ID_LABEL]

            blockedSims[id1] = {}
            for (id2, sim) in id2Sims.items():
                node_id_2 = input_target_graph.node[id2][NODE_ID_LABEL]

                if (node_id_1 in include_sources or node_id_2 in include_targets):
                    blockedSims[id1][id2] = sim
        '''

        self._logger.debug("Taking top %d link similarity", DEFAULT_MAX_LINKS_PER_NODE)
        for (id1, sims) in distances.items():
            sims = list(sims.items())
            sims.sort(reverse = True, key = operator.itemgetter(1))
            blockedSims[id1] = dict(sims[0:DEFAULT_MAX_LINKS_PER_NODE])

        for (id1, id2Sims) in blockedSims.items():
            for (id2, sim) in id2Sims.items():
                source_label = computeNodeLabel(input_source_graph.node[id1][NODE_ID_LABEL], NODE_MODIFIER_SOURCE)
                target_label = computeNodeLabel(input_target_graph.node[id2][NODE_ID_LABEL], NODE_MODIFIER_TARGET)

                attributes = {
                    WEIGHT_KEY: sim,
                    EDGE_TYPE_KEY: EDGE_TYPE_LINK,
                    SOURCE_GRAPH_KEY: COMPUTED_SOURCE_LOCAL_SIM,
                    OBSERVED_KEY: False
                }

                output_graph.add_edge(source_label, target_label, **attributes)

    # Just check the first node on each graph and make sure they match.
    # TODO(eriq): Variable feature pattern. Hint?
    def _discoverFeatures(self, *graphs):
        features = []

        if (len(graphs) == 0):
            return features

        # Fetch the initial features.
        for nodeId, data in graphs[0].nodes(data = True):
            for key in data:
                if (re.match(DEFAULT_FEATURE_PATTERN, key)):
                    features.append(key)
            break

        features.sort()

        # Ensure that all the features are in the other graph.
        for graph in graphs[1:]:
            for nodeId, data in graph.nodes(data = True):
                for feature in features:
                    if (feature not in data):
                        raise ValueError("Features are not consistent across graphs.")
                break

        return features

    # TODO(eriq): We should implement a can_accept() that ensures we only have a graph-matching problem dataset.

    metadata = d3m_metadata.metadata.PrimitiveMetadata({
        'id': 'da0405b0-2d6f-4107-94f6-658913c7cc70',
        'version': '0.0.1',
        'name': "Graph Transformer",
        'keywords': ['primitive', 'graph', 'dataset', 'transformer', 'PSL'],
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
