# -*- coding: utf-8 -*-
"""
Created on Sat Feb  3 23:05:54 2018

@author: thomas
"""

### imports ###################################################################
import numpy as np

### imports from ##############################################################
from numpy.linalg import norm, svd

###############################################################################
def fitPlane(XYZ):
    N = len(XYZ)
    X0 = np.ones((N, 1))
    X = np.hstack((XYZ, X0))
    
    U, D, Vt = svd(X, 0)
    V = Vt.T
    
    P = V[:, 3]
    norm_v = norm(P[:3])
    P = -np.sign(P[3]) * P / norm_v

    n = P[:3]
    a = -P[3]

    return n, a