# -*- coding: utf-8 -*-

import logging

import networkx

from pipesnake.base.abstract import Pipe
from pipesnake.base.abstract import Transformer
from pipesnake.pipe.parallel import ParallelPipe
from pipesnake.pipe.series import SeriesPipe

__all__ = [
    'to_graph',
    'draw_graph_on_file',
]


def _get_edges(item, heads=[], edges=[]):
    """Computes all the edges (connections) between transformers.

    This is a bit convoluted, but it does the job

    :param item: a :class:`Pipe` inherited object
    :param heads: used for recursion
    :param relations: used for recursion
    :return: last head, and the list of edges
    """
    if isinstance(item, ParallelPipe):
        new_heads = []
        for sub_item in item.transformers:
            current_head, _ = _get_edges(sub_item, heads, edges)
            new_heads.extend(current_head)
        return new_heads, _
    elif isinstance(item, SeriesPipe):
        current_head = heads
        for sub_item in item.transformers:
            current_head, _ = _get_edges(sub_item, current_head, edges)
        return current_head, _
    elif isinstance(item, Transformer):
        for head in heads:
            edges.append((head, item.name))
    else:
        raise Exception('Unexpected object type: {}'.format(type(item)))
    return [item.name], edges


def _get_nodes(item, nodes=[]):
    """Get the list of nodes (aka list of :class:`Transformer`) and their params

    :param item: a :class:`Pipe` inherited object
    :param nodes: used for recursion
    :return: the list of nodes names and their params
    """
    if isinstance(item, ParallelPipe) or isinstance(item, SeriesPipe):
        for sub_item in item.transformers:
            _get_nodes(sub_item, nodes)
    elif isinstance(item, Transformer):
        nodes.append((item.name, item.get_params()))
    else:
        raise Exception('Unexpected object type: {}'.format(type(item)))
    return nodes


def to_graph(pipe):
    """Create a NetworkX representation of a pipe

    :param pipe: a pipesnake pipe
    :return: a NetworkX graph
    """
    assert issubclass(type(pipe), Pipe), 'Mismatched type: expected Pipe got {0}'.format(type(pipe))

    graph = networkx.Graph()

    for node in _get_nodes(pipe, nodes=[]):
        graph.add_node(node[0], params=node[1])

    _, edges = _get_edges(pipe, heads=[], edges=[])
    for _from, _to in edges:
        graph.add_edge(_from, _to)

    return graph


def draw_graph_on_file(graph, filename='figure.png'):
    """Save a png file with the pipe graph

    :param graph: a NetworkX graph
    :param filename: a filename for the image

    .. todo:: It would be nice to have a nice layout for this
    """
    try:
        from matplotlib import pyplot
    except Exception as e:
        logging.error('matplotlib is not installed')
        return
    pos = networkx.spring_layout(graph)
    networkx.draw(graph, pos=pos, with_labels=True, node_color='skyblue', node_shape='.', alpha=0.65)
    pyplot.savefig(filename)
