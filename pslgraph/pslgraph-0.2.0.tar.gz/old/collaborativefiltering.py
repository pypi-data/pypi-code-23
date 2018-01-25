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

USER_COLUMN = 'user_id'
JOKE_COLUMN = 'item_id'
RATING_COLUMN = 'rating'

class CollaborativeFilteringTransformer(TransformerPrimitiveBase[Inputs, Outputs]):

    def __init__(self):
        pass

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> Outputs:
        assert(inputs is not None)

        dataDir = inputs


        userJokes = readHeaderCSV(os.path.join(dataDir, 'trainData.csv'), [USER_COLUMN, JOKE_COLUMN])

        users = [row[0] for row in userJokes]
        jokes = [row[1] for row in userJokes]
        ratings = [val[0] for val in readHeaderCSV(os.path.join(dataDir, 'trainTargets.csv'), [RATING_COLUMN])]

        userGraph = self._buildSourceGraph(users)
        jokeGraph = self._buildSourceGraph(jokes)
        ratingGraph = self._buildTargetGraph(users, jokes, ratings)

        # Add in some hints 

        # We know that it makes sense to compute the mean link prior
        for graph in [userGraph, jokeGraph, ratingGraph]:
            graph.hints[GRAPH_HINT_LINK_MEAN] = True

        # We know that computing the cosine similarity for edges make sense.
        userGraph.hints[GRAPH_HINT_EDGE_COSINE] = True
        jokeGraph.hints[GRAPH_HINT_EDGE_COSINE] = True

        return [userGraph, jokeGraph, ratingGraph]

    def _buildSourceGraph(self, items):
        graph = networkx.Graph()
        for item in items:
            graph.add_node(item, label = item)

        return BasicGraph(networkXGraph = graph)

    def _buildTargetGraph(self, users, jokes, ratings):
        assert(len(users) == len(jokes))
        assert(len(users) == len(ratings))

        # Normalize the ratings from [-10, 10] to [0, 1]
        ratings = [(rating + 10.0) / 20.0 for rating in ratings]

        graph = networkx.DiGraph()
        for i in range(len(users)):
            graph.add_node(users[i], label = users[i])
            graph.add_node(jokes[i], label = jokes[i])
            graph.add_edge(users[i], jokes[i], weight = ratings[i])

        return BasicGraph(networkXGraph = graph)
