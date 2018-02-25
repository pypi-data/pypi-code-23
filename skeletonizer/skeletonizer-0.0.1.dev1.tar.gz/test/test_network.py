import unittest
import copy

from skeletonizer.network import *


class SerialNetworkTest(unittest.TestCase):

    def setUp(self):
        # A simple network with two serial pipes of different length, and
        # three equal nodes.
        self.network = Network()
        self.n1 = Node("N1", 0.0, 0.0)
        self.n2 = Node("N2", 0.0, 0.0)
        self.n3 = Node("N3", 0.0, 0.0)

        self.p1 = Pipe("P1", self.n1, self.n2, 100, 200, 0.1)
        self.p2 = Pipe("P2", self.n2, self.n3, 300, 200, 0.1)

        self.network.add_nodes(self.n1, self.n2, self.n3)
        self.network.add_pipes(self.p1, self.p2)

    def test_is_serial(self):
        self.assertTrue(self.network.is_serial(self.p1, self.p2))

    def test_is_parallel(self):
        self.assertFalse(self.network.is_parallel(self.p1, self.p2))

    def test_merge_serial(self):
        self.assertIn(self.n2, self.network.nodes)

        # Merge serial pipes
        self.network.merge_serial(self.p1, self.p2)

        self.assertEqual(len(self.network.nodes), 2)
        self.assertEqual(len(self.network.pipes), 1)

        self.assertNotIn(self.n2, self.network.nodes)
        self.assertEqual(self.network.pipes[0].length, 400)
        self.assertEqual(self.network.pipes[0].diameter, 200)

    def test_merge_serial_demand_distribution(self):
        self.n1.demand = 1.0
        self.n2.demand = 2.0
        self.n3.demand = 3.0

        self.assertIn(self.n2, self.network.nodes)

        # Merge serial pipes
        self.network.merge_serial(self.p1, self.p2)

        # Flow is distributed with inverse ratio to pipe length
        self.assertEqual(self.n1.demand, 1.0 + 0.75 * 2.0)
        self.assertEqual(self.n3.demand, 3.0 + 0.25 * 2.0)

    def test_merge_parallel(self):
        with self.assertRaises(ParallelMergeOperationFailed):
            self.network.merge_parallel(self.p1, self.p2)


# TODO: ParallelNetworkTest


if __name__ == "__main__":
    unittest.main()
