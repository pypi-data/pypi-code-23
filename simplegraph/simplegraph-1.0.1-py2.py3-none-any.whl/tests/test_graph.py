
import unittest
from simplegraph import Graph, GraphValue

import data

class TestGraph(unittest.TestCase):
    def test_len(self):
        g = Graph()
        g.add('s', 'p', GraphValue('o1'))
        g.add('s', 'p', GraphValue('o2'))
        self.assertEqual(len(g), 2)

    def test_idempotency(self):
        g = Graph()
        g.add('s', 'p', GraphValue('o1'))
        g.add('s', 'p', GraphValue('o1'))
        self.assertEqual(len(g), 1)

    def test_get_by_subject(self):
        g = Graph()
        t = data.graph_a0()
        g.merge(t)
        g.merge(data.graph_a1())
        r = Graph()
        for s, p, o in g.get_by_subject('a0'):
            r.add(s, p, o)
        self.assertTrue(t.equals(r))

if __name__ == '__main__':
    unittest.main()
