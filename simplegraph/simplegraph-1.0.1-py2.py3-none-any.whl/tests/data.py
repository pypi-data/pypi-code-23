
from simplegraph import Graph, GraphValue

def graph_a0():
    g = Graph()
    g.add('a0', 'p', GraphValue('o0'))
    g.add('a0', 'p', GraphValue('o1'))
    g.add('a0', 'p', GraphValue('o2'))
    g.add('a0', 'q', GraphValue('o0'))
    g.add('a0', 'q', GraphValue('o1'))
    g.add('a0', 'q', GraphValue('o2'))
    return g

def graph_a1():
    g = Graph()
    g.add('a1', 'p', GraphValue('o0'))
    g.add('a1', 'p', GraphValue('o1'))
    g.add('a1', 'p', GraphValue('o2'))
    g.add('a1', 'q', GraphValue('o0'))
    g.add('a1', 'q', GraphValue('o1'))
    g.add('a1', 'q', GraphValue('o2'))
    return g

def graph_a2():
    g = Graph()
    g.add('a2', 'p', GraphValue('o0'))
    g.add('a2', 'p', GraphValue('o1'))
    g.add('a2', 'p', GraphValue('o2'))
    g.add('a2', 'q', GraphValue('o0'))
    g.add('a2', 'q', GraphValue('o1'))
    g.add('a2', 'q', GraphValue('o2'))
    return g