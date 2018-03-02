"""
.. module:: spine
   :synopsis: helper module for spine

"""

import vtkh
import numpy as np


def create2DSpline(pts, u=np.arange(0, 1.01, 0.01)):
    spline = vtkh.createParamSpline(pts, k=3)
    pts2 = vtkh.evalSpline(spline, u)
    return pts2
    
    
def calcSplineTangentSlopes(pts, u=np.arange(0, 1.01, 0.01)):
    spline, uPts = vtkh.createParamSpline(pts, k=3, retU=True)
    if u == 'only_pts':
        u = uPts
    der = vtkh.evalSplineDerivative(spline, u, der=1)
    return der
    
    
def calcInterlinesAngle(m1, m2):
    angles = np.rad2deg(np.arctan(np.abs((m1 - m2) / (1 + m1 * m2))))
    return angles