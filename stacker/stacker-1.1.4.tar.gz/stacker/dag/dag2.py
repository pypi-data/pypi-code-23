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
    def __init__(self, graph, node, existing_node):
        super(DuplicateNode, self).__init__(graph, node)
        self.existing_node = existing_node

    def __repr__(self):
        return "node '%s' already exists in graph." % self.node


class NodeHasDescendants(DAGNodeException):
    def __repr__(self):
        return "node '%s' has descendants." % self.node


class Node(object):
    def __init__(self, graph, name, parents=None, children=None):
        self.graph = graph
        self.name = name
        self.parents = parents or OrderedDict()
        self.children = children or OrderedDict()

    def add_parent(self, parent):
        parent._add_child(self)
        self.parents[parent.name] = parent

    def remove_parent(self, parent):
        parent._remove_child(self)
        del(self.parents[parent.name])

    def _add_child(self, child):
        self.children[child.name] = child

    def _remove_child(self, child):
        del(self.children[child.name])

    def descendants(self):
        descendants = OrderedDict()
        for child in self.children:
            descendants[child.name] = child
            descendants.update(child.descendants())
        return descendants

    @property
    def has_descendants(self):
        if self.children:
            return True
        return False

    def ancestors(self):
        ancestors = OrderedDict()
        for parent in self.parents:
            ancestors[parent.name] = parent
            ancestors.update(parent.ancestors())
        return ancestors

    @property
    def has_ancestors(self):
        if not self.parents:
            return True
        return False


class Graph(object):
    def __init__(self):
        self.reset_graph()

    def reset_graph(self):
        self.nodes = OrderedDict()

    def get_node(self, node):
        try:
            return self.nodes[node]
        except KeyError:
            raise NodeNotFound(self, node)

    def add_node(self, node_name):
        if node_name in self.nodes:
            raise DuplicateNode(self, node_name)

        node = Node(self, node_name)
        self.nodes[node_name] = node
        return node

    def add_node_if_not_exists(self, node_name, parents=None, children=None):
        try:
            return self.add_node(node_name, parents, children)
        except DuplicateNode as exc:
            return exc.existing_node

    def add_dependency(self, child_name, parent_name):
        child = self.get_node(child_name)
        parent = self.get_node(parent_name)
        child.add_parent(parent)

    def independent_nodes(self):
        nodes = []
        for node in self.nodes.itervalues():
            if not node.has_ancestors:
                nodes.append(node)
        return nodes

    def childless_nodes(self):
        nodes = []
        for node in self.nodes.itervalues():
            if not node.has_descendants:
                nodes.append(node)
        return nodes

    def delete_node(self, node_name):
        try:
            node = self.nodes[node_name]
        except KeyError:
            raise NodeNotFound(self, node_name)

        if node.has_descendants:
            raise NodeHasDescendants(self, node)

        for parent in node.parents.values():
            node.remove_parent(parent)

        del(self.nodes[node_name])
