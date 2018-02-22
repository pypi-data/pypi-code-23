# -*- coding: utf-8 -*-

### imports ###################################################################
import numpy as np
import unittest

### imports from ##############################################################
from some_math.geo.line_segment import LineSegment

###############################################################################
class TestLineSegment(unittest.TestCase):
    def test_00_LineSegment(self):
        ls = LineSegment()
        
        check = np.allclose(ls.X12, (1, 0, 0))
        self.assertTrue(check)
        
        
        
