# -*- coding: utf-8 -*-

### imports ###################################################################
import numpy as np

### imports from ##############################################################
from some_math.quaternion import Quaternion

###############################################################################
class Points3D(object):
    def __init__(self, xyz):
        self.X, self.Y, self.Z = xyz
        self.shape = self.X.shape

        self.X_flat = np.ravel(self.X)
        self.Y_flat = np.ravel(self.Y)
        self.Z_flat = np.ravel(self.Z)

    @property
    def XYZ(self):
        return np.vstack((self.X_flat, self.Y_flat, self.Z_flat)).T
       
    def rotate_v_v(self, v0, v1):
        q = Quaternion.from_v_v(v0, v1)
        R = q.as_rotation_matrix()
        XYZ = np.array(R * self.XYZ.T).T

        XYZ_tuple = np.hsplit(XYZ, 3)
        
        return Points3D(XYZ_tuple)