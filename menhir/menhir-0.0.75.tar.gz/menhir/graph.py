# Graph functions

# Graphs are modelled as a dict of edges from source node to a set of
# child nodes.
import logging
from copy import copy

log = logging.getLogger(__name__)


def root_nodes(graph, nodes):
    """Return the set of all nodes that are not dependencies of other nodes."""
    from functools import reduce
    nodes = set(nodes.keys())
    return reduce(set.difference, graph.values(), nodes)


def leaf_nodes(graph):
    """Return the set of all nodes that are not dependencies of other nodes."""
    from functools import reduce
    return reduce(set.union, map(set, graph.values()), set())


def dfs_visit(graph, node, state, pre_f, post_f, child_state_f=copy):
    """Visit all nodes in depth first order.

    pre_f is called on entry to the node, and returns an updated state.

    The state is passed to each child node, after being passed through
    child_state_f.  By default, child_state_f copies the state, so it
    is not shared between children.

    post_f is used to process all the child states.

    """
    log.debug('dfs_visit: %s %s %s', node, state, graph.get(node))
    state = pre_f(state, node)
    log.debug('dfs_visit after pre_f: %s', state)
    child_states = [
        dfs_visit(
            graph,
            child,
            child_state_f(state),
            pre_f,
            post_f,
            child_state_f=child_state_f
        )
        for child in graph.get(node, [])
    ]
    log.debug('dfs_visit after child_states: %s', child_states)
    return post_f(state, node, child_states)
