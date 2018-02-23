# -*- coding: utf-8 -*-

### imports ###################################################################
import unittest

### imports from ##############################################################
from some_math.geo.cuboid import Cuboid
from some_math.geo.plane import Plane

###############################################################################
class TestCuboid(unittest.TestCase):
    def test_00_cut(self):
        cuboid = Cuboid()
        plane = Plane(n=(0, 0, 1), a=0)
        
        cuts = cuboid.planeCut(plane)
        N = len(cuts)
        
        self.assertEqual(N, 5)

    def test_01_cut_vertex(self):
        cuboid = Cuboid()
        plane = Plane(n=(1, 1, 1), a=1)
        
        cuts = cuboid.planeCut(plane)
        N = len(cuts)
        
        self.assertEqual(N, 4)
        
    def test_02_no_cut(self):
        cuboid = Cuboid()
        plane = Plane(n=(0, 0, 1), a=5)
        
        cuts = cuboid.planeCut(plane)
        N = len(cuts)
        
        self.assertEqual(N, 0)
