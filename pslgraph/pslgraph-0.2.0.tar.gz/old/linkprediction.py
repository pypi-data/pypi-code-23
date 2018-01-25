from typing import *

from primitive_interfaces.unsupervised_learning import UnsupervisedLearnerPrimitiveBase

from .graphdata import GraphData
from .util import getLinksFromPSL
from .util import runPSL

# TODO(eriq): The input type needs some thinking.
#   For set_training_data() we only need the graph, and produce() we only need the node ids.

Params = TypeVar('Params')
Inputs = TypeVar('Inputs', bound = Tuple[GraphData, Sequence[Sequence[int]]])
Outputs = TypeVar('Outputs', bound = Sequence[Sequence[int]])

class PSLLinkPrediction(UnsupervisedLearnerPrimitiveBase[Inputs, Outputs, Params]):

    def __init__(self, include_all_edges = False) -> None:
        self._graphData = None
        self._include_all_edges = include_all_edges
        self._links = None

    def set_training_data(self, *, inputs: Inputs) -> None:
        assert(inputs is not None)
        assert(len(inputs) > 0)
        assert(inputs[0] is not None)

        self._graphData = inputs[0]

    def fit(self, *, timeout: float = None, iterations: int = None) -> None:
        if (self._graphData is None):
            raise "Call set_training_data() before fit()."

        # Convert the GML into the PSL format.
        self._graphData.write_psl_data(include_all_edges = self._include_all_edges)

        # Run the "unified" model in PSL.
        pslOutput = runPSL('unified')

        # Parse the output and save the links.
        self._links = getLinksFromPSL(pslOutput)

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> Outputs:
        if (self._links == None):
            raise "Call fit() before produce()."

        assert(inputs is not None)
        assert(len(inputs) == 2)
        assert(inputs[1] is not None)

        targets = inputs[1]

        if (len(targets) == 0):
            return

        # If there is only one identifier in the target, then give the other half of the best link.
        if (len(targets[0]) == 1):
            sourceIds = [val[0] for val in targets]
            return self._getBestTargets(sourceIds)
        # If there are two identifiers in the target, then give the weight of the link between them.
        elif (len(targets[0]) == 2):
            raise("TODO(eriq)")
        else:
            raise("Unknown type of target.")

    def _getBestTargets(self, sourceIds):
        # Get all the best links
        bestLinks = {}

        for (id1, links) in self._links.items():
            bestId = None
            bestScore = None

            for (id2, score) in links.items():
                if (bestScore is None or score > bestScore):
                    bestId = id2
                    bestScore = score

            bestLinks[id1] = (bestId, bestScore)

        results = []
        for sourceId in sourceIds:
            results.append(bestLinks[sourceId][0])

        return results

    def get_params(self) -> Params:
        pass

    def set_params(self, *, params: Params) -> None:
        pass
