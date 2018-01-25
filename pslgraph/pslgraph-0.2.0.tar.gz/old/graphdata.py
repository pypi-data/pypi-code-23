import csv

from scipy import sparse as sp
from d3m_types.base import Graph
import networkx
import numpy as np
import os

from .constants import *
from .util import writeTSV

class GraphData(Graph):
    """
    This is the concrete implementation of the D3M abstract type. This class is used by the PSLGraphPrimitive class to
    represtent the graph input and output data.
    A networkx graph may be passed in directly using the "direct_graph" param.
    
    This class inherits the following attributes

    Attributes
    ----------
    adjacency_matrix : scipy csr matrix

    _num_vertices : int
        Number of vertices

    _num_edges : int
        Number of edges

    _directed : boolean
        Declares if it is a directed graph or not

    _weighted : boolean
        Declares if it is a weighted graph or not

    _dangling_nodes : int numpy array
        Nodes with zero edges

    d : float64 numpy vector
        Degrees vector

    dn : float64 numpy vector
        Component-wise reciprocal of degrees vector

    d_sqrt : float64 numpy vector
        Component-wise square root of degrees vector

    dn_sqrt : float64 numpy vector
        Component-wise reciprocal of sqaure root degrees vector

    vol_G : float64 numpy vector
        Volume of graph

    components : list of sets
        Each set contains the indices of a connected component of the graph

    number_of_components : int
        Number of connected components of the graph

    bicomponents : list of sets
        Each set contains the indices of a biconnected component of the graph

    number_of_bicomponents : int
        Number of connected components of the graph

    core_numbers : dictionary
        Core number for each vertex

    In addition, direct access to an inderlying networkx graph is provided via the "_graph" attribute.
    """

    def __init__(self, filename = None, file_type = 'gml', separator = '\t', direct_graph = None):
        """
        Initializes the graph from a gml or a edgelist file and initializes the attributes of the class.

        Parameters
        ----------
        filename : string
            Name of the file, for example 'JohnsHopkins.edgelist' or 'JohnsHopkins.gml'.

        dtype : string
            Type of file. Currently only 'edgelist' and 'gml' are supported.
            Default = 'gml'

        separator : string
            used if file_type = 'edgelist'
            Default = '\t'
        """
        super().__init__(filename, file_type, separator)

        self._graph = None

        self.bicomponents = None
        self.number_of_bicomponents = -1
        self.components = None
        self.number_of_components = -1
        self.d = None
        self._dangling = -1
        self.dn = -1
        self.d_sqrt = -1
        self.dn_sqrt = -1
        self.vol_G = -1
        self.core_numbers = None

        if (direct_graph == None):
            self.read_graph(filename, file_type, separator)
        else:
            self._init_from_graph(direct_graph)

    def biconnected_components(self):
        """
        Computes the biconnected components of the graph. It stores the results in class attributes bicomponents
        and number_of_bicomponents. The user needs to call read the graph first before calling this
        function by calling the read_graph function from this class. This function calls Networkx.
        """

        if (self.bicomponents is not None):
            return

        self.bicomponents = list(networkx.biconnected_components(self._graph))
        self.number_of_bicomponents = len(self.bicomponents)

    def import_text(self, filename, separator):
        """
        Reads text from filename.
        """
        for line in csv.reader(open(filename), delimiter=separator, skipinitialspace=True):
            if line:
                yield line

    def connected_components(self):
        """
        Computes the connected components of the graph. It stores the results in class attributes components
        and number_of_components. The user needs to call read the graph
        first before calling this function by calling the read_graph function from this class.
        This function calls Networkx.
        """
        if (self.components is not None):
            return

        self.components = list(networkx.connected_components(self._graph))
        self.number_of_components = len(self.components)

        print('There are ', self.number_of_components, ' connected components in the graph')

    def compute_statistics(self):
        self._compute_statistics()
        
    def _compute_statistics(self, verbose = True):
        """
        Computes statistics for the graph. It updates the class attributes. The user needs to read the graph first before calling
        this method by calling the read_graph method from this class.
        """
        if (self.d is not None):
            return

        n = self._num_vertices

        self.d = np.ravel(self.adjacency_matrix.sum(axis=1))
        self._dangling = np.where(self.d == 0)[0]
        if self._dangling.shape[0] > 0:
            if (verbose):
                print('The following nodes have no outgoing edges:', self._dangling, '\n')
                print('These nodes are stored in the your_graph_object.dangling.')
                print('To avoid numerical difficulties we connect each dangling node to another randomly chosen node.')

            # TODO(eriq): Is this correct?
            self.adjacency_matrix = sp.lil_matrix(self.adjacency_matrix)

            for i in self._dangling:
                numbers = list(range(0, i)) + list(range(i + 1, n - 1))
                j = np.random.choice(numbers)
                self.adjacency_matrix[i, j] = 1
                self.adjacency_matrix[j, i] = 1

            self.adjacency_matrix = sp.csr_matrix(self.adjacency_matrix)

            self.d = np.ravel(self.adjacency_matrix.sum(axis=1))

        self.dn = 1.0 / self.d
        self.d_sqrt = np.sqrt(self.d)
        self.dn_sqrt = np.sqrt(self.dn)
        self.vol_G = np.sum(self.d)

    def core_number(self):
        """
        Returns the core number for each vertex. A k-core is a maximal
        subgraph that contains nodes of degree k or more. The core number of a node
        is the largest value k of a k-core containing that node. The user needs to
        call read the graph first before calling this function by calling the read_graph
        function from this class. The output can be accessed from the graph object that
        calls this function. It stores the results in class attribute core_numbers.
        """

        if (self.core_numbers is not None):
            return

        self.core_numbers = networkx.core_number(self._graph)

    def is_disconnected(self):
        """
        The output can be accessed from the graph object that calls this function.

        Checks if the graph is a disconnected graph. It prints the result as a comment and
        returns True if the graph is disconnected, or false otherwise. The user needs to
        call read the graph first before calling this function by calling the read_graph function from this class.
        This function calls Networkx.

        Returns
        -------
        True
             If connected

        False
             If disconnected
        """
        if self.d == []:
            print('The graph has to be read first.')
            return

        self.connected_components()

        if self.number_of_components > 1:
            print('The graph is a disconnected graph.')
            return True
        else:
            print('The graph is not a disconnected graph.')
            return False

    def read_graph(self, filename, file_type='gml', separator='\t'):
        """
        Reads the graph from a gml or a edgelist file and initializes the class attribute adjacency_matrix.

        Parameters
        ----------
        filename : string
            Name of the file, for example 'JohnsHopkins.edgelist' or 'JohnsHopkins.gml'.

        dtype : string
            Type of file. Currently only 'edgelist' and 'gml' are supported.
            Default = 'gml'

        separator : string
            used if file_type = 'edgelist'
            Default = '\t'
        """

        self._graph_filename = filename
        self._init_from_graph(networkx.read_gml(filename))

    def _init_from_graph(self, nxGraph):
        self._graph = nxGraph

        self.adjacency_matrix = networkx.adjacency_matrix(self._graph).astype(np.float64)
        self._num_edges = networkx.number_of_edges(self._graph)
        self._num_vertices = networkx.number_of_nodes(self._graph)
        self._directed = networkx.is_directed(self._graph)
        self._compute_statistics(verbose = False)

    def write_graph(self, path):
        networkx.write_gml(self._graph, path)

    def write_psl_data(self, base_path = DEFAULT_DATA_DIR, include_all_edges = False):
        """
        Decompose the graph into data for a PSL link prediction model.
        Every unobserved link (where a link exists, but has the property: 'observed': False) is a target.
        """

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
