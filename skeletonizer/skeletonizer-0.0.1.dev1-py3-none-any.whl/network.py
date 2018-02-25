from collections import OrderedDict
from typing import List, Union, Tuple
from math import sqrt

# TODO: CMH or CMS? Preference to use SI internally


class NetworkOperationDenied(Exception):
    pass


class SerialMergeOperationFailed(NetworkOperationDenied):
    pass


class ParallelMergeOperationFailed(NetworkOperationDenied):
    pass


class Node:
    def __init__(self, name: str, elevation: float, demand: float, **kwargs):
        self.name = name
        self.elevation = elevation
        self.demand = demand

        self._pipes = []

    def can_remove(self) -> bool:
        """
        Any special properties of the node that make it not removable. This
        method is called from the can_remove_node() on the network level,
        which does other checks as well.

        :returns: Whether or not Node can be removed.
        """
        return True

    @property
    def pipes(self) -> List['Pipe']:
        """
        List of pipes to which this node is attached.
        """
        return self._pipes

    # TODO: Should we move this to the network class? We don't have a merge
    # method for pipes, so why should we have one for nodes.
    def merge(self, n: 'Node', f=1.0) -> None:
        """
        Merge this node with another node.

        Add fraction f of demand of node n to this node's demand Override this
        function if you also want to do something special with elevation, or
        other properties you may have added.
        """
        self.demand += n.demand * f

    def __str__(self):
        return self.name


class NetworkObject:
    """
    Base class for any objects in the network, like pipes, valves, etc.
    """

    def __init__(self, name):
        self.name = name
        self._nodes = []

    def can_remove(self) -> bool:
        return False

    @property
    def nodes(self) -> List[Node]:
        return self._nodes

    def __str__(self):
        return self.name


class Pipe(NetworkObject):

    def __init__(self, name, n1, n2, length, diameter, roughness, **kwargs):
        super().__init__(name)

        self.n1 = n1
        self.n2 = n2
        self.length = length
        self.diameter = diameter
        self.roughness = roughness

        self._nodes = [n1, n2]

        # Profile is a list of tuples (spos, elevation).
        # spos is position along pipe length.
        # Start and end elevation are taken from nodes when querying the
        # appropriate function get_profile()
        self.profile = []

    # Pipes can be removed by default
    def can_remove(self):
        return True

    def other_node(self, n: Node):  # Returns the node that is not equal to n
        if n not in self._nodes:
            raise Exception("Node {} is not connected to this pipe.".format(n))
        else:
            return self.n1 if n is self.n2 else self.n2

    def profile_add(self, sdistance, elevation):
        self.profile.append((sdistance, elevation))

    def is_loop(self):
        return self.n1 is self.n2

    def common_node(self, p: 'Pipe'):
        common_nodes = set(self.nodes).intersection(set(p.nodes))
        if len(common_nodes) != 1:
            return None
        else:
            return common_nodes.pop()

    def replace_node(self, node: Node, other: Node) -> None:
        i = self._nodes.index(node)
        self._nodes[i] = other


class Network:
    # TODO: Make sure that nodes and pipes can only be accessed through
    # iterators and other functions that can be overridden
    def __init__(self):
        # Make sure that we are working with ordered dicts, to keep things deterministic
        self._nodes = []
        self._pipes = []

    # Private
    def __update_connections(self):
        for n in self._nodes:
            n._pipes = []

        for p in self._pipes:
            for n in p.nodes:
                n._pipes.append(p)

    def __iterate_pairs(array):
        for i, a in enumerate(array):
            for j in range(i+1, len(array)):
                yield (a, b)

    #
    def stats(self):
        return {"n_pipes": len(pipes), "n_nodes": len(nodes)}

    # Node methods
    @property
    def nodes(self):
        return self._nodes

    def get_node_pairs(self):
        yield __iterate_pairs(nodes)

    def add_nodes(self, *nodes):
        for n in nodes:
            self._nodes.append(n)

    def can_remove_node(self, n):
        # Examples include nodes connected to special pipes/valves/special components
        # or nodes with a special name prefix.
        if n.can_remove():
            return True
        else:
            return False

    # Pipe methods
    @property
    def pipes(self):
        return self._pipes

    def get_pipe_pairs(self) -> List[Pipe]:
        yield __iterate_pairs(pipes)

    def add_pipes(self, *pipes: List[Pipe]):
        for p in pipes:
            self._pipes.append(p)
            for x in p._nodes:
                x._pipes.append(p)

    def can_remove_pipe(self, p: Pipe):
        if p.can_remove():
            return True
        else:
            return False

    def is_serial(self, a: Pipe, b: Pipe):
        common = a.common_node(b)

        if common is None:
            return False
        elif len(common.pipes) > 2:
            return False
        elif a.is_loop() or b.is_loop():
            return False
        else:
            return True

    def is_parallel(self, a: Pipe, b: Pipe) -> bool:
        # Check if they have exactly two nodes in common
        common = set(a.nodes).intersection(set(b.nodes))
        if len(common) != 2:
            return False
        elif a.is_loop() or b.is_loop():
            return False
        else:
            return True

    def can_merge_serial(self, a: Pipe, b: Pipe):
        common = a.common_node(b)

        if not self.is_serial(a, b):
            return False
        elif not self.can_remove_node(common):
            return False
        elif not self.can_remove_pipe(a) or not self.can_remove_pipe(b):
            return False
        else:
            return True

    def can_merge_parallel(self, a: Pipe, b: Pipe):
        if not self.is_parallel(a, b):
            return False
        elif not self.can_remove_pipe(a) or not self.can_remove_pipe(b):
            return False
        else:
            return True

    def merge_serial(self, a: Pipe, b: Pipe) -> Tuple[Node, Pipe]:
        """
        Tries to merge two serial pipes in the network.

        :returns: The common node and pipe that have been removed from the network.

        .. caution::

            - Changes in diameter cause reflections in transient analysis.
              Merging pipes into one removes these reflections and as such
              changes results.
            - If the demand of the common node is relatively large, a large
              portion of the flow will now go through both pipes or instead none
              at all (demand is spread to the edges). This can result in
              different head losses (and transient behavior as well).
            - Some output methods do not support pipe profile. So if the common
              node is located a lot higher than the outer nodes, a possible
              critical point in the system (low pressure/cavitation) can be
              missed.
        """
        common = a.common_node(b)

        if common is None:
            raise SerialMergeOperationDenied(
                "Tried to serially merge two pipes that are not connected.")

        if not self.is_serial(a, b):
            raise SerialMergeOperationDenied(
                "Tried to serially merge two pipes that are not serial pipes.")

        if not self.can_merge_serial(a, b):
            raise SerialMergeOperationDenied(
                "Tried to serially merge two pipes that are not allowed to be merged.")

        node_a = a.other_node(common)  # Node unique to pipe a
        node_b = b.other_node(common)  # Node unique to pipe b

        # Merge demands. The longer the pipe, the less demand
        demandf = a.length / (a.length + b.length)
        node_a.merge(common, 1.0 - demandf)
        node_b.merge(common, demandf)

        # Preserve length
        new_length = a.length + b.length
        # Preserve volume
        new_diam = sqrt((a.length * a.diameter**2 + b.length * b.diameter**2)/new_length)
        # length weighted k/D
        new_roughness = ((a.roughness * a.length / a.diameter + b.roughness * b.length / b.diameter)
                         * new_diam/new_length)

        # Add removed node's height to profile
        a.profile_add(a.length, common.elevation)

        # Set the new values
        a.length = new_length
        a.diameter = new_diam
        a.roughness = new_roughness

        a.replace_node(common, node_b)
        self._nodes.remove(common)
        self._pipes.remove(b)

        # TODO: Should we also return the original a?
        # TODO: Don't forget to copy vertices in epanet
        return common, b

    def merge_parallel(self, a: Pipe, b: Pipe) -> Pipe:
        """
        Tries to merge two parallel pipes in the network.

        :returns: The pipe that has been removed from the network.

        .. caution::

            - If length differs by a lot, travel time of shock wave probably
              differs as well

            - Equivalent diameter of two short parallel pipes might be too
              large to do serial merging with afterwards
        """
        if not self.is_parallel(a, b):
            raise ParallelMergeOperationFailed(
                "Tried to parallel merge two pipes that are not parallel pipes.")

        if not self.can_merge_parallel(a, b):
            raise ParallelMergeOperationFailed(
                "Tried to parallel merge two pipes that are not allowed to be merged.")

        # Keep total surface area the same
        diameter = sqrt(a.diameter**2 + b.diameter**2)

        # Harmonically average the length and roughness (k-value)
        length = 1.0/(1.0/a.length + 1.0/b.length)
        roughness = 1.0/(1.0/a.roughness + 1.0/b.roughness)

        # Set the new values
        a.length = length
        a.roughness = roughness
        a.diameter = diameter

        self._pipes.remove(b)

        # TODO: Don't forget to remove vertices in epanet
        return b
