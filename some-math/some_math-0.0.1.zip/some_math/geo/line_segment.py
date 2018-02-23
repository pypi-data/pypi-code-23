# -*- coding: utf-8 -*-

import numpy as np

###############################################################################
class LineSegment:
    def __init__(self, X1 = (0, 0, 0), X2 = (1,0,0)):
        self.X1 = np.array(X1)
        self.X2 = np.array(X2)
        self.X12 = self.X2 - self.X1
