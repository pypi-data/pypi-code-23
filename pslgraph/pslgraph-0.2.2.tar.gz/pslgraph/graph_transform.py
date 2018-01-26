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
import sklearn

from . import config
from .constants import *
from .networkx import Graph, DiGraph
from .util import computeNodeLabel, get_logger, set_logging_level

# TODO(eriq): Hyperparam?
DEFAULT_MIN_COSINE_SIM = 0.50
DEBUG_BAIL_COUNT = 100

# TODO(eriq): Change the output to just a graph once there is officially metadata on it.
Inputs = d3m_metadata.container.List[Graph]
Outputs = d3m_metadata.container.List[Graph]

# TODO(eriq): We need a way to cut down these graphs, they can get pretty big.
#   Maybe we can sample around the explicit targets?

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
        metadata = inputs.metadata.clear(metaInfo, for_value = outputs, source = self)
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

        self._logger.debug("Build a graph with hints: %s.", hints)

        self._process_graph(output_graph, input_source_graph)
        self._process_graph(output_graph, input_target_graph)

        explicit_targets = []
        if (link_graph is not None):
            explicit_targets = self._process_links(output_graph, link_graph)

        if (hints[GRAPH_HINT_LINK_LOCAL_SIM]):
            self._compute_local_sim_link_weights(output_graph, input_source_graph, input_target_graph, explicit_targets)

        if (hints[GRAPH_HINT_LINK_MEAN]):
            self._compute_mean_link_weights(output_graph, input_source_graph, input_target_graph, explicit_targets)

        if (hints[GRAPH_HINT_EDGE_COSINE][0]):
            self._compute_cosine_edge_weights(output_graph, input_source_graph, explicit_targets)

        if (hints[GRAPH_HINT_EDGE_COSINE][1]):
            self._compute_cosine_edge_weights(output_graph, input_target_graph, explicit_targets)

        # Ensure that explicit targets are included.
        self._logger.debug("Adding explicit targets (%d).", len(explicit_targets))
        for (source_label, target_label) in explicit_targets:
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
    def _process_graph(self, output_graph, input_graph):
        # First add all the nodes.
        for (label, data) in input_graph.nodes(data = True):
            attributes = {
                SOURCE_GRAPH_KEY: data[SOURCE_GRAPH_KEY],
                NODE_ID_LABEL: data[NODE_ID_LABEL],
            }
            output_graph.add_node(label, **attributes)

        # Now add all the edges.
        for (source_label, target_label) in input_graph.edges():
            # Disallow self edges.
            if (source_label == target_label):
                continue

            weight = 1.0
            if (WEIGHT_KEY in input_graph[source_label][target_label]):
                weight = input_graph[source_label][target_label][WEIGHT_KEY]

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
        for (source_label, target_label, data) in link_graph.edges(data = True):
            if (TARGET_KEY in data and data[TARGET_KEY]):
                # This link is an explicit target, make sure to include it in targets.
                targets.append((source_label, target_label))
            else:
                # This link is observed.
                weight = 1.0
                if (WEIGHT_KEY in link_graph[source_label][target_label]):
                    weight = float(link_graph[source_label][target_label][WEIGHT_KEY])

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
            GRAPH_HINT_EDGE_COSINE: [False, False],
        }

        # First check for hints from each graph.
        for i in range(len(graphs)):
            graph_hints = graphs[i].metadata.query([])['hints']

            if (not graph_hints):
                continue

            if (GRAPH_HINT_LINK_LOCAL_SIM in graph_hints):
                hints[GRAPH_HINT_LINK_LOCAL_SIM] = hints[GRAPH_HINT_LINK_LOCAL_SIM] or graph_hints[GRAPH_HINT_LINK_LOCAL_SIM]

            if (GRAPH_HINT_LINK_MEAN in graph_hints):
                hints[GRAPH_HINT_LINK_MEAN] = hints[GRAPH_HINT_LINK_MEAN] or graph_hints[GRAPH_HINT_LINK_MEAN]

            if (GRAPH_HINT_EDGE_COSINE in graph_hints and i < 2):
                hints[GRAPH_HINT_EDGE_COSINE][i] = graph_hints[GRAPH_HINT_EDGE_COSINE]

        return hints

    # Look for node attributes that look like features get the distance (normalized into similarity) between them.
    # TODO(eriq): Make blocking tunable.
    # TODO(eriq): Features from hints
    # TODO(eriq): Where are some target links that we want to make sure are included.
    def _compute_local_sim_link_weights(self, output_graph, input_source_graph, input_target_graph, explicit_targets):
        self._logger.debug("Computing local link similarity")

        features = self._discoverFeatures(input_source_graph, input_target_graph)

        # {source_label: {target_label: [distance, ...], ...}, ...}
        distances = {}

        for feature in features:
            min_val = None
            max_val = None

            for source_label in input_source_graph.nodes():
                count = 0
                for target_label in input_target_graph.nodes():
                    # Only calcualte distance for links not already observed in the output graph.
                    if (output_graph.has_edge(source_label, target_label) and output_graph[source_label][target_label][OBSERVED_KEY]):
                        continue

                    distance = abs(input_source_graph.node[source_label][feature] - input_target_graph.node[target_label][feature])

                    if (min_val is None or distance < min_val):
                        min_val = distance

                    if (max_val is None or distance > max_val):
                        max_val = distance

                    if (source_label not in distances):
                        distances[source_label] = {}

                    if (target_label not in distances[source_label]):
                        distances[source_label][target_label] = []

                    distances[source_label][target_label].append(distance)

                    count += 1
                    if self._debug_run_fast and count == int(DEFAULT_MAX_LINKS_PER_NODE / 2):
                        break

            # Just do a min/max normalization into a similarity.
            # TODO(eriq): Better normalization here can go a long way.
            range_val = float(max_val - min_val)
            for (source_label, id2Distances) in distances.items():
                for (target_label, pairDistances) in id2Distances.items():
                    distance = pairDistances[-1]
                    pairDistances[-1] = (1.0 - min(1.0, max(0.0, float(distance - min_val) / range_val)))

        # Just get the mean or the normalized values, but we could also do
        # something like a logistic regression on the raw values.
        # now distances = {source_label: {target_label: nomral distance, ...}, ...}
        for (source_label, target_sims) in distances.items():
            for (target_label, pairSims) in target_sims.items():
                distances[source_label][target_label] = float(sum(pairSims)) / len(pairSims)

        # For blocking purposes, choose the top N similarities for each node.
        blockedSims = {}

        ''' TODO(eriq): This is pretty costly (750k in test data). Can we make it cheaper?
        # Before we block, include all information from both sides of explicit targets.
        include_sources = {explicit_target[0] for explicit_target in explicit_targets}
        include_targets = {explicit_target[1] for explicit_target in explicit_targets}
        for (source_label, target_sims) in distances.items():
            node_id_1 = input_source_graph.node[source_label][NODE_ID_LABEL]

            blockedSims[source_label] = {}
            for (target_label, sim) in target_sims.items():
                node_id_2 = input_target_graph.node[target_label][NODE_ID_LABEL]

                if (node_id_1 in include_sources or node_id_2 in include_targets):
                    blockedSims[source_label][target_label] = sim
        '''

        self._logger.debug("Taking top %d link similarity", DEFAULT_MAX_LINKS_PER_NODE)
        for (source_label, sims) in distances.items():
            sims = list(sims.items())
            sims.sort(reverse = True, key = operator.itemgetter(1))
            blockedSims[source_label] = dict(sims[0:DEFAULT_MAX_LINKS_PER_NODE])

        for (source_label, target_sims) in blockedSims.items():
            for (target_label, sim) in target_sims.items():
                attributes = {
                    WEIGHT_KEY: sim,
                    EDGE_TYPE_KEY: EDGE_TYPE_LINK,
                    SOURCE_GRAPH_KEY: COMPUTED_SOURCE_LOCAL_SIM,
                    OBSERVED_KEY: False
                }

                output_graph.add_edge(source_label, target_label, **attributes)

    # Put a computed edge over every pair of nodes
    # (that do not already have one).
    # First get the mean of all observed link a source/target is
    # already involved in.
    # Then get every pair without an observed label and assign it the
    # mean of the source and target mean.
    def _compute_mean_link_weights(self, output_graph, input_source_graph, input_target_graph, explicit_targets):
        self._logger.debug("Computing mean link weights")

        # {label: [running sum, count], ...}
        source_weights = {}
        target_weights = {}

        # Sum up all the link weights.
        for (source_label, target_label, data) in output_graph.edges(data = True):
            if (data[EDGE_TYPE_KEY] != EDGE_TYPE_LINK or not data[OBSERVED_KEY]):
                continue

            if (WEIGHT_KEY not in data):
                raise ValueError("No weight for (%s, %s)." % (source_label, target_label))

            if (source_label not in source_weights):
                source_weights[source_label] = [0.0, 0]

            if (target_label not in target_weights):
                target_weights[target_label] = [0.0, 0]

            source_weights[source_label][0] += data[WEIGHT_KEY]
            source_weights[source_label][1] += 1

            target_weights[target_label][0] += data[WEIGHT_KEY]
            target_weights[target_label][1] += 1

        # Average the weights out.
        for source_label in source_weights:
            source_weights[source_label] = source_weights[source_label][0] / source_weights[source_label][1]

        for target_label in target_weights:
            target_weights[target_label] = target_weights[target_label][0] / target_weights[target_label][1]

        # Assign a link to every pair that does not already have one.
        for source_label in input_source_graph.nodes():
            count = 0
            for target_label in input_target_graph.nodes():
                if (output_graph.has_edge(source_label, target_label) and output_graph[source_label][target_label][OBSERVED_KEY]):
                    continue

                weight = None
                if (source_label in source_weights):
                    weight = source_weights[source_label]

                if (target_label in target_weights):
                    if (weight is None):
                        weight = target_weights[target_label]
                    else:
                        weight = (weight + target_weights[target_label]) / 2.0

                if (weight is None):
                    continue

                attributes = {
                    WEIGHT_KEY: weight,
                    EDGE_TYPE_KEY: EDGE_TYPE_LINK,
                    SOURCE_GRAPH_KEY: COMPUTED_SOURCE_MEAN,
                    OBSERVED_KEY: False
                }
                output_graph.add_edge(source_label, target_label, **attributes)

                count += 1
                if (self._debug_run_fast and count == DEFAULT_MAX_LINKS_PER_NODE):
                    break

    # Calclate the cosine similarity between two nodes in the same graph
    # (which means we will be inserting an edge).
    # Use the weights of observed links as the vectors to compare.
    # We will only calculate one diagonal since these edges are undirected.
    # Remember that this is within one graph, so "source" and "target" here
    # refer to the terminal nodes of an edge (not link).
    def _compute_cosine_edge_weights(self, output_graph, input_graph, explicit_targets):
        self._logger.debug("Computing cosine edge weights")

        # First, build the sparse vectors of obsereved edge weights.
        # [source_label, ...] (1-1 with graph_weights).
        graph_ids = []
        # [{target_label: weight, ...}, ...]
        graph_weights = []

        for source_label in input_graph.nodes():
            weights = {}

            for target_label in output_graph[source_label]:
                data = output_graph[source_label][target_label]

                if (data[EDGE_TYPE_KEY] == EDGE_TYPE_LINK and data[OBSERVED_KEY] and WEIGHT_KEY in data):
                    weights[target_label] = data[WEIGHT_KEY]

            graph_ids.append(source_label)
            graph_weights.append(weights)

        # Turn the mappings into sparse vectors.
        graph_vectors = sklearn.feature_extraction.DictVectorizer().fit_transform(graph_weights)

        # Calculate the pairwise cosine similarities.
        outter_loop_count = 0
        for index1 in range(len(graph_ids)):
            outter_loop_count += 1
            if (self._debug_run_fast and outter_loop_count >= DEBUG_BAIL_COUNT):
                break

            source_label = graph_ids[index1]
            added_count = 0
            inner_loop_count = 0

            for index2 in range(index1 + 1, len(graph_ids)):
                target_label = graph_ids[index2]

                inner_loop_count += 1
                if (self._debug_run_fast and inner_loop_count >= DEBUG_BAIL_COUNT):
                    break

                # Skip if we already have an observed edge.
                if (output_graph.has_edge(source_label, target_label) and output_graph[source_label][target_label][OBSERVED_KEY]):
                    continue

                cosine_sim = sklearn.metrics.pairwise.cosine_similarity(graph_vectors[index1], graph_vectors[index2])[0][0]

                if (cosine_sim < DEFAULT_MIN_COSINE_SIM):
                    continue

                attributes = {
                    WEIGHT_KEY: cosine_sim,
                    EDGE_TYPE_KEY: EDGE_TYPE_EDGE,
                    SOURCE_GRAPH_KEY: COMPUTED_SOURCE_COSINE,
                    OBSERVED_KEY: False
                }
                output_graph.add_edge(source_label, target_label, **attributes)

                # TODO(eriq): Need to enforce a max number of edges even out of debug.

                added_count += 1
                if (self._debug_run_fast and added_count >= DEFAULT_MAX_LINKS_PER_NODE):
                    break

    # Just check the first node on each graph and make sure they match.
    # TODO(eriq): Variable feature pattern. Hint?
    def _discoverFeatures(self, *graphs):
        features = []

        if (len(graphs) == 0):
            return features

        # Fetch the initial features.
        for id, data in graphs[0].nodes(data = True):
            for key in data:
                if (re.match(DEFAULT_FEATURE_PATTERN, key)):
                    features.append(key)
            break

        features.sort()

        # Ensure that all the features are in the other graph.
        for graph in graphs[1:]:
            for id, data in graph.nodes(data = True):
                for feature in features:
                    if (feature not in data):
                        raise ValueError("Features are not consistent across graphs.")
                break

        return features

    # TODO(eriq): We should implement a can_accept() that ensures we only have a graph-matching problem dataset.

    metadata = d3m_metadata.metadata.PrimitiveMetadata({
        # Required
        'id': 'da0405b0-2d6f-4107-94f6-658913c7cc70',
        'version': config.VERSION,
        'name': 'Graph Transformer',
        'description': 'Take in some graphs respectivley describing two graphs and (optinally) targets between those graphs, and produce a single unified graph with potentially more computed edges.',
        'python_path': 'd3m.primitives.pslgraph.GraphTransformer',
        'primitive_family': d3m_metadata.metadata.PrimitiveFamily.DATA_TRANSFORMATION,
        'algorithm_types': [
            d3m_metadata.metadata.PrimitiveAlgorithmType.COMPUTER_ALGEBRA,
        ],
        'source': {
            'name': config.D3M_PERFORMER_TEAM,
            'uris': [ config.REPOSITORY ]
        },

        # Optional
        'keywords': [ 'preprocessing', 'primitive', 'graph', 'transformer' ],
        'installation': [ config.INSTALLATION ],
        'location_uris': [],
        'precondition': [ d3m_metadata.metadata.PrimitiveEffects.NO_MISSING_VALUES ],
        'effects': [ d3m_metadata.metadata.PrimitiveEffects.NO_MISSING_VALUES ],
        'hyperparms_to_tune': []
    })
