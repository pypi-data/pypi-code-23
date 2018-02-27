
from .graph import GraphValue

def domain(schema, graph):
    for s in schema.get_by_predicate('domain'):
        for g in list(graph.get_by_predicate(s[0])):
            graph.add(g[0], '@type', GraphValue(s[2]))

def range(schema, graph):
    for s in schema.get_by_predicate('range'):
        for g in list(graph.get_by_predicate(s[0])):
            if g[2].is_ref:
                graph.add(g[2].value, '@type', GraphValue(s[2]))

def inverseOf(schema, graph):
    for s in schema.get_by_predicate('inverseOf'):
        if s[2].is_ref:
            for g in list(graph.get_by_predicate(s[0])):
                if g[2].is_ref:
                    graph.add(g[2].value, s[2].value, GraphValue(g[0], True))
