
# encoding: utf-8

"""A type to represent, query, and manipulate a Uniform Resource Identifier."""

from .graph import Graph, GraphValue, print_graph
from .rules import domain, range, inverseOf

__all__ = [
            'Graph',
            'GraphValue',
            'print_graph',
]