# -*- coding: utf-8 -*-


import unittest

from pipesnake.pipe import ParallelPipe
from pipesnake.pipe import SeriesPipe
from pipesnake.transformers.selector import ColumnSelector
from pipesnake.utils.graph import to_graph


class TestGraph(unittest.TestCase):
    def test_graph(self):
        pipe = SeriesPipe(transformers=[
            ParallelPipe(transformers=[
                ColumnSelector(x_cols=['x_1', 'x_2', 'x_3', 'x_4', ], y_cols=['y_1', ], name='1'),
                ColumnSelector(x_cols=['x_3', ]),
            ]),
            ColumnSelector(x_cols=['x_1_1', ], y_cols=['y_1_1', ]),
        ])
        graph = to_graph(pipe)
        for node in graph:
            print(node, graph.node[node]['params'])
