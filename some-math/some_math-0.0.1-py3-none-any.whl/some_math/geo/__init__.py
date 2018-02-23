# -*- coding: utf-8 -*-

### imports ###################################################################
import numpy as np

### imports from ##############################################################
from numpy.linalg import norm

###############################################################################
def cart2sph(v):
    """Convert from cartesian to spherical coordinates
    """
    
    x, y, z = v
    
    XsqPlusYsq = x**2 + y**2
    r = np.sqrt(XsqPlusYsq + z**2)               # r
    elev = np.arctan2(z, np.sqrt(XsqPlusYsq))     # theta
    az = np.arctan2(y,x)                           # phi
    
    return r, elev, az

###############################################################################
def isLeft(A, B, C, D):
    AB = B - A
    AC = C - A
    AD = D - A
    n = np.cross(AB, AC)
    l = np.cross(AB, AD)

    sgn = np.sign(np.dot(n,l))

    return bool(sgn + 1)

###############################################################################
def normalized(v):
        v = np.array(v)
        v = v / norm(v)
        
        return v
