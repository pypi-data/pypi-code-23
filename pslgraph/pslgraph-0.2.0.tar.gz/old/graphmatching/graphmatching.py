# A primitive to transform graphmatching-style problems into the types of graphs that the graph transformer can consume.
# This is a fairly trivial transformer.

import os
from typing import *

import networkx
from primitive_interfaces.transformer import TransformerPrimitiveBase

from .basicgraph import BasicGraph
from .constants import *
from .util import readHeaderCSV

# TODO(eriq): I am not sure how the other TA1/TA2 primitives pick up data like this.
#  For now, we will just take the path to the data dir.
Inputs = TypeVar('Inputs', bound = str)
# Graph1, Graph2, Targets
Outputs = TypeVar('Outputs', bound = Tuple[BasicGraph, BasicGraph, BasicGraph])

class GraphMatchingTransformer(TransformerPrimitiveBase[Inputs, Outputs]):

    def __init__(self):
        pass

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> Outputs:
        assert(inputs is not None)

        dataDir = inputs

        graph1 = BasicGraph()
        graph1.read_graph(os.path.join(dataDir, 'raw_data', 'G1.gml'), relabel = NODE_ID_LABEL)

        graph2 = BasicGraph()
        graph2.read_graph(os.path.join(dataDir, 'raw_data', 'G2.gml'), relabel = NODE_ID_LABEL)

        observedSources = [val[0] for val in readHeaderCSV(os.path.join(dataDir, 'trainData.csv'), ['G1.nodeID'])]
        observedTargets = [val[0] for val in readHeaderCSV(os.path.join(dataDir, 'trainTargets.csv'), ['G2.nodeID'])]

        targetsGraph = self._buildTargetGraph(observedSources, observedTargets)

        # Add in some hints 
        # We know that it makes sense to compute the local feature based similarity of the links.
        for graph in [graph1, graph2, targetsGraph]:
            graph.hints[GRAPH_HINT_LINK_LOCAL_SIM] = True

        return graph1, graph2, targetsGraph

    def _buildTargetGraph(self, observedSources, observedTargets):
        assert(len(observedSources) == len(observedTargets))

        graph = networkx.DiGraph()
        for i in range(len(observedSources)):
            graph.add_node(observedSources[i], label = observedSources[i])
            graph.add_node(observedTargets[i], label = observedTargets[i])
            graph.add_edge(observedSources[i], observedTargets[i], weight = 1.0)

        return BasicGraph(networkXGraph = graph)
