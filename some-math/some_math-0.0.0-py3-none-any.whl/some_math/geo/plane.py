# -*- coding: utf-8 -*-

### imports ###################################################################
import numpy as np

### imports from ##############################################################
from numpy.linalg import norm

###############################################################################
class Plane:
    def __init__(self, n = (1, 0, 0), a = 0):
        ### normal vector
        self.n = np.array(n)
        self.n = self.n / norm(self.n)
        nx, ny, nz = self.n

        ### distance from origin
        self.a = a
        
        ### angles
        self.azimut = np.arctan2(ny, nx)
        self.theta = np.arccos(nz)


    def setAzimut(self, azimut):
        self.azimut = azimut
        self.updateNormal()


    def setTheta(self, theta):
        self.theta = theta
        self.updateNormal()

    def setDistance(self, a):
        self.a = a
        
    def updateNormal(self):
        nxy = np.sin(self.theta) 
        nx =  nxy * np.cos(self.azimut)
        ny =  nxy * np.sin(self.azimut)      
        nz = np.cos(self.theta)

        self.n = np.array([nx, ny, nz])
        
    def LineSegmentCut(self, ls):
        n12 = np.dot(self.n, ls.X12)
        
        if not np.isclose(n12, 0):
            c = (self.a - np.dot(self.n, ls.X1)) / n12
        else:
            c = np.nan
        
        if (c >= 0 and c <= 1):
            Xc = ls.X1 + c * ls.X12
        else:
            Xc = None
        
        return Xc