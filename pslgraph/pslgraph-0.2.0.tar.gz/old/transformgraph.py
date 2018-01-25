import operator
import re
from typing import *

from d3m_types.base import Graph
from primitive_interfaces.graph import GraphTransformerPrimitiveBase
import networkx
import numpy
import sklearn.feature_extraction
import sklearn.metrics.pairwise

from .basicgraph import BasicGraph
from .constants import *

# We will only accept sequences of two or three graphs.
# If a third graph is specified, it is treated as observed links between the two graphs.
Inputs = TypeVar('Inputs', bound=Sequence[Graph])

# We output a single graph that is all ready for PSL decomposition and inference.
# Details:
#   - Nodes
#       - Each is marked with the graph it came from (1 or 2)
#       - Each has a label set to: "graphId::nodeId"
#   - Edges
#       - "Edges" (edges between nodes in the same graph) have some weight based on node similarity (zero weight edges are left out).
#       - "Links" (edges between nodes in different graphs) have a weight and the "type: observed" property.
Outputs = TypeVar('Outputs', bound = BasicGraph)

# TODO(eriq): Details on the third graph.
#  It should be directed.
#  The source will be traeated as if it is in the first graph, the target will be treated as if it is in the second.

DEFAULT_MAX_LINKS_PER_NODE = 100
DEFAULT_MAX_COMPUTED_EDGES = 500
DEFAULT_FEATURE_PATTERN = r'f\d+'

class PSLGraphTransformer(GraphTransformerPrimitiveBase[Inputs, Outputs]):

    # TODO(eriq): Explain these options more.
    def __init__(self,
            computeEdgeCosine = None, computeLinkLocalSim = None, computeLinkMean = None,
            maxEdgesPerNode = DEFAULT_MAX_LINKS_PER_NODE, maxComputedEdges = DEFAULT_MAX_COMPUTED_EDGES,
            featurePattern = DEFAULT_FEATURE_PATTERN) -> None:
        self._computeEdgeCosine = computeEdgeCosine
        self._computeLinkLocalSim = computeLinkLocalSim
        self._computeLinkMean = computeLinkMean
        self._maxLinksPerNode = maxEdgesPerNode
        self._maxComputedEdges = maxComputedEdges
        self._featurePattern = re.compile(featurePattern)

    # Looks for hints and reconcile them with the construction options.
    def _checkHints(self, graphs):
        hints = {
            GRAPH_HINT_LINK_LOCAL_SIM: False,
            GRAPH_HINT_LINK_MEAN: False,
            # We can get different hints about each input graph.
            GRAPH_HINT_EDGE_COSINE: (False, False),
        }

        # First check for hints from each graph.
        for i in range(len(graphs)):
            if (not graphs[i].hints):
                continue

            if (GRAPH_HINT_LINK_LOCAL_SIM in graphs[i].hints):
                hints[GRAPH_HINT_LINK_LOCAL_SIM] = graphs[i].hints[GRAPH_HINT_LINK_LOCAL_SIM]

            if (GRAPH_HINT_LINK_MEAN in graphs[i].hints):
                hints[GRAPH_HINT_LINK_MEAN] = graphs[i].hints[GRAPH_HINT_LINK_MEAN]

            if (GRAPH_HINT_EDGE_COSINE in graphs[i].hints and i < 2):
                hints[GRAPH_HINT_EDGE_COSINE][i] = graphs[i].hints[GRAPH_HINT_EDGE_COSINE]

        # Now override any options with the settings from construction.
        if (self._computeLinkLocalSim):
            hints[GRAPH_HINT_LINK_LOCAL_SIM] = self._computeLinkLocalSim

        if (self._computeLinkMean):
            hints[GRAPH_HINT_LINK_MEAN] = self._computeLinkMean

        if (self._computeEdgeCosine):
            hints[GRAPH_HINT_EDGE_COSINE] = (self._computeEdgeCosine, self._computeEdgeCosine)

        return hints

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> Outputs:
        # Ensure that we only have two or three input graphs.
        assert(len(inputs) == 2 or len(inputs) == 3)

        graph = networkx.Graph()

        hints = self._checkHints(inputs[0:3])

        self._processGraph(graph, inputs[0], 1)
        self._processGraph(graph, inputs[1], 2)

        if (len(inputs) == 3):
            self._processLinks(graph, inputs[2])

        if (hints[GRAPH_HINT_LINK_LOCAL_SIM]):
            self._computeLocalSimLinkWeights(graph, inputs[0], inputs[1])

        if (hints[GRAPH_HINT_LINK_MEAN]):
            self._computeMeanLinkWeights(graph, inputs[0], inputs[1])

        for i in range(2):
            if (hints[GRAPH_HINT_EDGE_COSINE][i]):
                self._computeCosineEdgeWeights(graph, inputs[i], i + 1)

        return BasicGraph(networkXGraph = graph)

    # Add the nodes and edges from a single graph.
    def _processGraph(self, outputGraph, inputGraph, graphId):
        # First add all the nodes.
        for nodeId in inputGraph.nodes():
            attributes = {SOURCE_GRAPH_KEY: graphId}
            outputGraph.add_node(self._getNodeId(graphId, nodeId), **attributes)

        # Now add all the edges.
        for (source, target) in inputGraph.edges():
            # Disallow self edges.
            if (source == target):
                continue

            weight = 1.0
            if (WEIGHT_KEY in inputGraph[source][target]):
                weight = inputGraph[source][target][WEIGHT_KEY]

            attributes = {WEIGHT_KEY: weight, EDGE_TYPE_KEY: EDGE_TYPE_EDGE, OBSERVED_KEY: True}
            outputGraph.add_edge(self._getNodeId(graphId, source), self._getNodeId(graphId, target), **attributes)

    def _processLinks(self, outputGraph, inputGraph):
        # All the nodes should already exist in each respective graph.
        for (source, target) in inputGraph.edges():
            weight = 1.0
            if (WEIGHT_KEY in inputGraph[source][target]):
                weight = inputGraph[source][target][WEIGHT_KEY]

            attributes = {WEIGHT_KEY: weight, EDGE_TYPE_KEY: EDGE_TYPE_LINK, OBSERVED_KEY: True}
            outputGraph.add_edge(self._getNodeId(1, source), self._getNodeId(2, target), **attributes)

    def _getNodeId(self, graphId, nodeId):
        return ("%s::%s" % (str(graphId), str(nodeId)))

    # TODO(eriq): This needs more testing with a better dataset (r60 (Jester)).

    # Calclate the cosine similarity between two nodes in the same graph (this is an edge).
    # Use the weights of observed links as the vectors to compare.
    # We will only calculate one diagonal since these edges are undirected.
    def _computeCosineEdgeWeights(self, outputGraph, inputGraph, graphId):
        # First build the sparse vectors of obsereved edge weights.
        graphIds = []
        # [{outputId2: weight, ...}, ...]
        graphWeights = []

        for id1 in inputGraph.nodes():
            outputId1 = self._getNodeId(graphId, id1)
            weights = {}

            for outputId2 in outputGraph[outputId1]:
                data = outputGraph[outputId1][outputId2]
                if (data[EDGE_TYPE_KEY] == EDGE_TYPE_LINK and data[OBSERVED_KEY] and WEIGHT_KEY in data):
                    weights[outputId2] = data[WEIGHT_KEY]

            graphIds.append(outputId1)
            graphWeights.append(weights)

        # Turn the mappings into sparse vectors.
        graphVectors = sklearn.feature_extraction.DictVectorizer().fit_transform(graphWeights)

        # Calculate the pairwise cosine similarities.
        newEdges = []
        for (index1, outputId1) in enumerate(graphIds):
            for (index2, outputId2) in enumerate(graphIds):
                if (outputId1 >= outputId2):
                    continue

                # Skip if we already have an observed edge.
                if (outputGraph.has_edge(outputId1, outputId2) and outputGraph[outputId1][outputId2][OBSERVED_KEY]):
                    continue

                cosineSim = sklearn.metrics.pairwise.cosine_similarity(graphVectors[index1], graphVectors[index2])[0][0]

                # Don't bother with negative values.
                # Just clip similarity to [0, 1] (cosine sim range it [-1, 1]).
                if (cosineSim < 0):
                    continue

                newEdges.append((cosineSim, outputId1, outputId2))

        # Sort by best cosine sim and take the top ones.
        newEdges = sorted(newEdges)[0:self._maxComputedEdges]

        for (sim, outputId1, outputId2) in newEdges:
            attributes = {WEIGHT_KEY: sim, EDGE_TYPE_KEY: EDGE_TYPE_EDGE, SOURCE_GRAPH_KEY: COMPUTED_SOURCE_COSINE, OBSERVED_KEY: False}
            outputGraph.add_edge(outputId1, outputId2, **attributes)

    # Look for node attributes that look like features get the distance (normalized into similarity) between them.
    def _computeLocalSimLinkWeights(self, outputGraph, inputGraph1, inputGraph2):
        features = self._discoverFeatures(inputGraph1, inputGraph2)

        # {id1: {id2: [distance, ...], ...}, ...}
        # id1 < id2
        distances = {}

        for feature in features:
            minVal = None
            maxVal = None

            for id1 in inputGraph1.nodes():
                for id2 in inputGraph2.nodes():
                    # Only calcualte distance for links not already observed in the output graph.
                    outputId1 = self._getNodeId(1, id1)
                    outputId2 = self._getNodeId(2, id2)
                    if (outputGraph.has_edge(outputId1, outputId2) and outputGraph[outputId1][outputId2][OBSERVED_KEY]):
                        continue
                    
                    distance = abs(inputGraph1.node[id1][feature] - inputGraph2.node[id2][feature])

                    if (minVal is None or distance < minVal):
                        minVal = distance

                    if (maxVal is None or distance > maxVal):
                        maxVal = distance

                    if (id1 not in distances):
                        distances[id1] = {}

                    if (id2 not in distances[id1]):
                        distances[id1][id2] = []

                    distances[id1][id2].append(distance)

            # Just do a min/max normalization into a similarity.
            # TODO(eriq): Better normalization here can go a long way.
            rangeVal = float(maxVal - minVal)
            for (id1, id2Distances) in distances.items():
                for (id2, pairDistances) in id2Distances.items():
                    distance = pairDistances[-1]
                    pairDistances[-1] = (1.0 - min(1.0, max(0.0, float(distance - minVal) / rangeVal)))

        # Just get the mean or the normalized values, but we could also do
        # something like a logistic regression on the raw values.
        for (id1, id2Sims) in distances.items():
            for (id2, pairSims) in id2Sims.items():
                distances[id1][id2] = float(sum(pairSims)) / len(pairSims)

        blockedSims = {}

        # For blocking purposes, choose the top N similarities for each node.
        for (id1, sims) in distances.items():
            sims = list(sims.items())
            sims.sort(reverse = True, key = operator.itemgetter(1))
            blockedSims[id1] = dict(sims[0:self._maxLinksPerNode])

        for (id1, id2Sims) in blockedSims.items():
            for (id2, sim) in id2Sims.items():
                attributes = {WEIGHT_KEY: sim, EDGE_TYPE_KEY: EDGE_TYPE_LINK, SOURCE_GRAPH_KEY: COMPUTED_SOURCE_LOCAL_SIM, OBSERVED_KEY: False}
                outputGraph.add_edge(self._getNodeId(1, id1), self._getNodeId(2, id2), **attributes)

    # Get the average link weight for all nodes participating in a link.
    # Remember that graph1 nodes will always be sources and graph2 nodes will always be destinations.
    # We are only considering observed links.
    def _computeMeanLinkWeights(self, outputGraph, inputGraph1, inputGraph2):
        # {id: [weight, ...], ...}
        sourceWeights = {}
        destWeights = {}

        # Sum up all the link weights.
        for (source, dest, data) in outputGraph.edges(data = True):
            if (data[EDGE_TYPE_KEY] == EDGE_TYPE_LINK and data[OBSERVED_KEY] and WEIGHT_KEY in data):
                if (source not in sourceWeights):
                    sourceWeights[source] = []

                if (dest not in destWeights):
                    destWeights[dest] = []

                sourceWeights[source].append(data[WEIGHT_KEY])
                destWeights[dest].append(data[WEIGHT_KEY])

        # Average the weights out.
        for source in sourceWeights:
            sourceWeights[source] = numpy.mean(sourceWeights[source])

        for dest in destWeights:
            destWeights[dest] = numpy.mean(destWeights[dest])

        # Every link that does not already 
        for id1 in inputGraph1.nodes():
            for id2 in inputGraph2.nodes():
                # Only put in mean edges for links not already observed in the output graph.
                outputId1 = self._getNodeId(1, id1)
                outputId2 = self._getNodeId(2, id2)
                if (outputGraph.has_edge(outputId1, outputId2) and outputGraph[outputId1][outputId2][OBSERVED_KEY]):
                    continue

                weights = []
                if (outputId1 in sourceWeights):
                    weights.append(sourceWeights[outputId1])

                if (outputId2 in destWeights):
                    weights.append(destWeights[outputId2])

                if (len(weights) == 0):
                    continue

                attributes = {WEIGHT_KEY: numpy.mean(weights), EDGE_TYPE_KEY: EDGE_TYPE_LINK, SOURCE_GRAPH_KEY: COMPUTED_SOURCE_MEAN, OBSERVED_KEY: False}
                outputGraph.add_edge(outputId1, outputId2, **attributes)

    # Just check the first node on each graph and make sure they match.
    def _discoverFeatures(self, graph1, graph2):
        features = []

        # Fetch the initial features.
        for nodeId, data in graph1.nodes(data = True):
            for key in data:
                if (self._featurePattern.match(key)):
                    features.append(key)
            break

        features.sort()

        # Ensure that all the features are in the other graph.
        for nodeId, data in graph2.nodes(data = True):
            for feature in features:
                if (feature not in data):
                    raise("Features are not consistent across graphs.")
            break

        return features
