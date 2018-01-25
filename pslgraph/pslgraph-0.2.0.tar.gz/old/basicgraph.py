import csv

from d3m_types.base import Graph
import networkx
import os

from .constants import *
from .util import writeTSV

'''
A simple implementation of the D3M abstract graph type.
This graph is not meant for analysis, only for data storage/passing.
As such, all inherited computation-centric methods and attributes are left unimplemented.
An additional property: 'hints' is also added to allow graph constructors to pass on any insights made during graph construction.
'''
class BasicGraph(Graph):
    def __init__(self, networkXGraph = None, hints = {}):
        super().__init__(None)

        # We only worrying about syncing hints on initialization (__init__ / read()) and write().
        self.hints = hints

        if (networkXGraph is not None):
            self._init_from_graph(networkXGraph)

    def biconnected_components(self):
        raise('Unsupported Operation')

    def import_text(self, filename, separator):
        raise('Unsupported Operation')

    def connected_components(self):
        raise('Unsupported Operation')

    def compute_statistics(self):
        raise('Unsupported Operation')
        
    def core_number(self):
        raise('Unsupported Operation')

    def is_disconnected(self):
        raise('Unsupported Operation')

    def read_graph(self, filename, relabel = None, file_type = 'gml', separator = '\t'):
        if (file_type != 'gml'):
            raise("BasicGraph only supports reading from gml files.")

        self._graph_filename = filename

        label = 'label'
        if (relabel is not None):
            label = relabel

        graph = networkx.read_gml(filename, label = label)

        if (relabel is not None):
            # NetworkX will not relabel the nodes sometimes, so we will ensure the relabeling happens.
            # If they actually did relabel, then this will do nothing.
            mapping = {}
            for nodeId in graph.nodes():
                mapping[nodeId] = graph.node[nodeId][relabel]
            networkx.relabel_nodes(graph, mapping, copy = False)

        self._init_from_graph(graph)

    def _init_from_graph(self, nxGraph):
        self._graph = nxGraph
        # Shadow some networkx functionality.
        self.node = self._graph.node

        self._directed = networkx.is_directed(self._graph)

        # See if there are any attributes (hints) attached to this graph.
        self.hints.update(self._graph.graph)

    def write_graph(self, path):
        # Make sure we add any hints.
        self._graph.graph.update(self.hints)

        networkx.write_gml(self._graph, path)

    # Shadow some networkx functionality.

    def nodes(self, data = False):
        return self._graph.nodes(data = data)

    def edges(self, data = False):
        return self._graph.edges(data = data)

    def __getitem__(self, key):
        return self._graph[key]

    '''
    Decompose the graph into data for a PSL link prediction model.
    Every unobserved link (where a link exists, but has the property: 'observed': False) is a target.
    '''
    def write_psl_data(self, base_path = DEFAULT_DATA_DIR, include_all_edges = False):
        os.makedirs(base_path, exist_ok = True)

        self._write_predicate_graph(os.path.join(base_path, GRAPH1_PREDICATE_FILENAME), 1)
        self._write_predicate_graph(os.path.join(base_path, GRAPH2_PREDICATE_FILENAME), 2)
        self._write_predicate_edge(os.path.join(base_path, EDGE1_PREDICATE_FILENAME), 1)
        self._write_predicate_edge(os.path.join(base_path, EDGE2_PREDICATE_FILENAME), 2)
        self._write_predicate_link_prior(os.path.join(base_path, LINK_PRIOR_PREDICATE_FILENAME))
        self._write_predicate_link_observed(os.path.join(base_path, LINK_PREDICATE_OBS_FILENAME))

        if (include_all_edges):
            self._write_predicate_link_target_all(os.path.join(base_path, LINK_PREDICATE_TARGET_FILENAME))
        else:
            self._write_predicate_link_target(os.path.join(base_path, LINK_PREDICATE_TARGET_FILENAME))

    def _write_predicate_graph(self, path, graphId):
        rows = []

        for (id, data) in self._graph.nodes(data = True):
            if (data[SOURCE_GRAPH_KEY] != graphId):
                continue
            rows.append([str(id)])

        writeTSV(path, rows)

    def _write_predicate_edge(self, path, graphId):
        rows = []

        for (source, target, data) in self._graph.edges(data = True):
            # Skip links.
            if (data[EDGE_TYPE_KEY] != EDGE_TYPE_EDGE):
                continue

            # Skip edges that do not come from out target graph.
            if (self._graph.node[source][SOURCE_GRAPH_KEY] != graphId):
                continue

            # Edges are undirected.
            rows.append([str(source), str(target), str(data[WEIGHT_KEY])])
            rows.append([str(target), str(source), str(data[WEIGHT_KEY])])

        writeTSV(path, rows)

    def _write_predicate_link_observed(self, path):
        rows = []

        for (source, target, data) in self._graph.edges(data = True):
            # Skip edges.
            if (data[EDGE_TYPE_KEY] != EDGE_TYPE_LINK):
                continue

            # Skip links that are not observed.
            if (not data[OBSERVED_KEY]):
                continue

            # Make sure graph 1 comes first.
            if (source > target):
                source, target = target, source

            rows.append([str(source), str(target), str(data[WEIGHT_KEY])])

        writeTSV(path, rows)

    def _write_predicate_link_prior(self, path):
        rows = []

        for (source, target, data) in self._graph.edges(data = True):
            # Skip edges.
            if (data[EDGE_TYPE_KEY] != EDGE_TYPE_LINK):
                continue

            # Skip observed links.
            # Since observed links are not targets, they have no prior.
            if (data[OBSERVED_KEY]):
                continue

            # Make sure graph 1 comes first.
            if (source > target):
                source, target = target, source

            rows.append([str(source), str(target), str(data[WEIGHT_KEY])])

        writeTSV(path, rows)

    def _write_predicate_link_target(self, path):
        rows = []

        for (source, target, data) in self._graph.edges(data = True):
            # Skip edges.
            if (data[EDGE_TYPE_KEY] != EDGE_TYPE_LINK):
                continue

            # Skip observed links.
            if (data[OBSERVED_KEY]):
                continue

            # Make sure graph 1 comes first.
            if (source > target):
                source, target = target, source

            rows.append([str(source), str(target)])

        writeTSV(path, rows)

    # Write every possible link that has not been observed.
    def _write_predicate_link_target_all(self, path):
        for (id1, data1) in self._graph.nodes(data = True):
            if (data1[SOURCE_GRAPH_KEY] != 1):
                continue

            for (id2, data2) in self._graph.nodes(data = True):
                if (data2[SOURCE_GRAPH_KEY] != 2):
                    continue

                # Skip any observed links
                if (self._graph.has_edge(id1, id2) and self._graph[id1][id2][OBSERVED_KEY]):
                    continue

                rows.append([str(id1), str(id2)])

        writeTSV(path, rows)
