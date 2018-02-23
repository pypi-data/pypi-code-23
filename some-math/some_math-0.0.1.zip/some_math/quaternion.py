# -*- coding: utf-8 -*-
"""
Created on Tue Apr  4 08:46:39 2017

@author: twagner
"""

### imports ###################################################################
import numpy as np

### imports from ##############################################################
from numpy.linalg import norm

###############################################################################
class Quaternion:
    """Quaternions for 3D rotations"""
    def __init__(self, x):
        self.x = np.asarray(x, dtype=float)

        
    @classmethod
    def from_v_theta(cls, v, theta):
        """
        Construct quaternion from unit vector v and rotation angle theta
        """
        theta = np.asarray(theta)
        v = np.asarray(v)
        
        s = np.sin(0.5 * theta)
        c = np.cos(0.5 * theta)
        vnrm = np.sqrt(np.sum(v * v))

        q = np.concatenate([[c], s * v / vnrm])
        return cls(q)

        
    @classmethod
    def from_v(cls, v):
        """
        Convert vector v into quaternion
        """
        q = np.concatenate(([0], v))
        return cls(q)


    @classmethod
    def from_v_v(cls, v0, v1):
        """
        Construct quaternion for rotation of unit vector v0 to v1
        """

        v0 = v0 / norm(v0) 
        v1 = v1 / norm(v1)

        if not np.allclose(v0, v1):
            v0_x_v1 = np.cross(v0, v1)
            sin_theta = norm(v0_x_v1)
            n_rot = v0_x_v1 / sin_theta
        
            cos_theta = np.dot(v0, v1)
            theta = np.arccos(cos_theta)
            
            q = Quaternion.from_v_theta(n_rot, theta)
        else:
            q = Quaternion((1, 0, 0, 0))
        
        return q

        
    @classmethod
    def inverse(cls, q):
        y = np.copy(q.x)
        y[1:] = - y[1:]

        return cls(y)

        
    def __repr__(self):
        return "Quaternion:\n" + self.x.__repr__()

        
    def __mul__(self, other):
        # multiplication of two quaternions.
        prod = self.x[:, None] * other.x

        return self.__class__([
            (prod[0, 0] - prod[1, 1] - prod[2, 2] - prod[3, 3]),
            (prod[0, 1] + prod[1, 0] + prod[2, 3] - prod[3, 2]),
            (prod[0, 2] + prod[2, 0] + prod[3, 1] - prod[1, 3]),
            (prod[0, 3] + prod[3, 0] + prod[1, 2] - prod[2, 1])
        ])

                                
    def as_v_theta(self):
        """Return the v, theta equivalent of the (normalized) quaternion"""
        # compute theta
        norm = np.sqrt((self.x ** 2).sum(0))
        theta = 2 * np.arccos(self.x[0] / norm)

        if np.isclose(theta, 0.0):
            v = np.array((0, 0, 1))
        else:
            # compute the unit vector
            v = np.array(self.x[1:], order='F', copy=True)
            v /= np.sqrt(np.sum(v ** 2, 0))

        return v, theta

        
    def as_rotation_matrix(self):
        """Return the rotation matrix of the (normalized) quaternion"""
        v, theta = self.as_v_theta()
        c = np.cos(theta)
        s = np.sin(theta)

        return np.matrix([
            [
                v[0] * v[0] * (1. - c) + c,
                v[0] * v[1] * (1. - c) - v[2] * s,
                v[0] * v[2] * (1. - c) + v[1] * s
            ],
            [
                v[1] * v[0] * (1. - c) + v[2] * s,
                v[1] * v[1] * (1. - c) + c,
                v[1] * v[2] * (1. - c) - v[0] * s
            ],
            [
                v[2] * v[0] * (1. - c) - v[1] * s,
                v[2] * v[1] * (1. - c) + v[0] * s,
                v[2] * v[2] * (1. - c) + c
            ]
        ])

        
    def spherical(self):
        x = self.x[1]
        y = self.x[2]
        z = self.x[3]

        r_xy_sq = x**2 + y**2
        r_xy = np.sqrt(r_xy_sq)
        r = np.sqrt(r_xy_sq + z**2)
        elev = np.arctan2(z, r_xy)      # theta
        az = np.arctan2(y, x)           # phi

        return r, elev, az
