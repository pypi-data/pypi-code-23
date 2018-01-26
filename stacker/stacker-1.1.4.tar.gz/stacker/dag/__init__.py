import logging
from copy import deepcopy
from collections import deque

logger = logging.getLogger(__name__)

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


class DAGException(Exception):
    def __init__(self, graph):
        self.graph = graph


class DAGValidationError(DAGException):
    pass


class DAGNodeException(DAGException):
    def __init__(self, graph, node):
        super(DAGNodeException, self).__init__(graph)
        self.node = node


class NodeNotFound(DAGNodeException):
    def __repr__(self):
        return "node '%s' does not exist in graph." % self.node


class DuplicateNode(DAGNodeException):
    def __repr__(self):
        return "node '%s' already exists in graph." % self.node


class DAGEdgeException(DAGException):
    def __init__(self, graph, parent_node, child_node):
        super(DAGEdgeException, self).__init__(graph)
        self.parent_node = parent_node
        self.child_node = child_node


class EdgeNotFound(DAGEdgeException):
    def __repr__(self):
        return "edge between '%s' and '%s' does not exist." % (
            self.parent_node, self.child_node
        )


class NoIndependentNodes(DAGValidationError):
    pass


class LoopFound(DAGValidationError):
    pass


class DAG(object):
    """ Directed acyclic graph implementation. """

    def __init__(self):
        """ Construct a new DAG with no nodes or edges. """
        self.reset_graph()

    def add_node(self, node_name, graph=None):
        """ Add a node if it does not exist yet, or error out. """
        if not graph:
            graph = self.graph
        if node_name in graph:
            raise DuplicateNode(graph, node_name)
        graph[node_name] = set()

    def add_node_if_not_exists(self, node_name, graph=None):
        try:
            self.add_node(node_name, graph=graph)
        except DuplicateNode:
            pass

    def delete_node(self, node_name, graph=None):
        """ Deletes this node and all edges referencing it. """
        if not graph:
            graph = self.graph
        if node_name not in graph:
            raise NodeNotFound(graph, node_name)
        graph.pop(node_name)

        for node, edges in graph.iteritems():
            if node_name in edges:
                edges.remove(node_name)

    def delete_node_if_exists(self, node_name, graph=None):
        try:
            self.delete_node(node_name, graph=graph)
        except NodeNotFound:
            pass

    def add_edge(self, parent_node, child_node, graph=None):
        """ Add an edge (dependency) between the specified nodes. """
        if not graph:
            graph = self.graph

        if parent_node not in graph:
            raise NodeNotFound(graph, parent_node)
        if child_node not in graph:
            raise NodeNotFound(graph, child_node)

        # TODO: Should we do this on every add_edge? Performance issue
        test_graph = deepcopy(graph)
        test_graph[parent_node].add(child_node)
        is_valid, message = self.validate(test_graph)

        if is_valid:
            graph[parent_node].add(child_node)
        else:
            raise DAGValidationError(message)

    def delete_edge(self, parent_node, child_node, graph=None):
        """ Delete an edge from the graph. """
        if not graph:
            graph = self.graph
        if child_node not in graph.get(parent_node, []):
            raise EdgeNotFound(graph, parent_node, child_node)
        graph[parent_node].remove(child_node)

    def transpose(self, graph=None):
        """ Builds a new graph with the edges reversed. """
        if not graph:
            graph = self.graph
        transposed = DAG()

        for node in graph:
            transposed.add_node(node)

        for parent_node, children in graph.items():
            # for each edge A -> B, transpose it so that B -> A
            for child_node in children:
                transposed.add_edge(child_node, parent_node)
        return transposed

    def parents(self, node, graph=None):
        """ Returns a list of all predecessors of the given node """
        if graph is None:
            graph = self.graph
        return [graph[key] for key in graph[node]]

    def children(self, node, graph=None):
        """ Returns a list of all nodes this node has edges towards. """
        if graph is None:
            graph = self.graph
        if node not in graph:
            raise NodeNotFound(node)
        return list(graph[node])

    def descendants(self, node, graph=None):
        """Returns a list of all nodes ultimately downstream
        of the given node in the dependency graph, in
        topological order."""
        if graph is None:
            graph = self.graph
        nodes = [node]
        nodes_seen = set()
        i = 0
        while i < len(nodes):
            children = self.children(nodes[i], graph)
            for child in children:
                if child not in nodes_seen:
                    nodes_seen.add(child)
                    nodes.append(child)
            i += 1

        return [
            n for n in self.topological_sort(graph=graph)
            if n in nodes_seen
        ]

    def filter(self, nodes, graph=None):
        """ Returns a new DAG with only the given nodes and their
        dependencies.
        """

        if graph is None:
            graph = self.graph
        dag = DAG()

        # Add only the nodes we need.
        for node in nodes:
            dag.add_node_if_not_exists(node)
            for descendant in self.descendants(node, graph=graph):
                dag.add_node_if_not_exists(descendant)

        # Now, rebuild the graph for each node that's present.
        for node in dag.graph:
            try:
                dag.graph[node] = graph[node]
            except KeyError:
                raise NodeNotFound(graph, node)

        return dag

    def all_leaves(self, graph=None):
        """ Return a list of all leaves (nodes with no downstreams) """
        if graph is None:
            graph = self.graph
        return [key for key in graph if not graph[key]]

    def from_dict(self, graph_dict):
        """ Reset the graph and build it from the passed dictionary.

        The dictionary takes the form of {node_name: [directed edges]}
        """

        self.reset_graph()

        for node, children in graph_dict.iteritems():
            self.add_node(node)
            if not isinstance(children, list):
                raise TypeError("dict values must be list")
            for child in children:
                self.add_edge(node, child)

    def reset_graph(self):
        """ Restore the graph to an empty state. """
        self.graph = OrderedDict()

    def independent_nodes(self, graph=None):
        """ Returns a list of all nodes in the graph with no dependencies. """
        if graph is None:
            graph = self.graph

        dependent_nodes = set()
        for dependent_list in graph.values():
            for dependent in dependent_list:
                dependent_nodes.add(dependent)

        return list(set(graph) - dependent_nodes)

    def topological_sort(self, graph=None):
        """ Returns a topological ordering of the DAG.

        Raises an error if this is not possible (graph is not valid).
        """
        if graph is None:
            graph = self.graph

        # First calculate in_degree, or number of descendants per node
        in_degree = {}
        for u in graph:
            in_degree[u] = 0

        for u in graph:
            for v in graph[u]:
                in_degree[v] += 1

        # Add all nodes with no descendants
        queue = deque()
        for u in in_degree:
            if in_degree[u] == 0:
                queue.appendleft(u)

        sorted_graph = []
        while queue:
            u = queue.pop()
            sorted_graph.append(u)
            for v in graph[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.appendleft(v)

        if len(sorted_graph) == len(graph):
            return sorted_graph
        else:
            raise LoopFound(graph)

    def size(self):
        return len(self.graph)

    def validate(self, graph=None):
        """ Returns (Boolean, message) of whether DAG is valid. """
        if graph is None:
            graph = self.graph

        if len(self.independent_nodes(graph)) == 0:
            raise NoIndependentNodes(graph)
        try:
            self.topological_sort(graph)
        except ValueError as e:
            return (False, e.message)
        return (True, 'valid')
