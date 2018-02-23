# -*- coding: utf-8 -*-

### imports ###################################################################
import numpy as np

###############################################################################
def findPointsAbove(points, n, a):
    '''find points above a plane defined by Hessian Form n * x = a
       n: normal vector
       a: distance from origin
    '''

    b = np.dot(n, points.transpose())

    iSelect = np.where(b > a)
    pointsAbove = points[iSelect, :].squeeze()

    return pointsAbove


def findPointsBelow(points, n, a):
    '''find points below a plane defined by Hessian Form n * x = a
       n: normal vector
       a: distance from origin
    '''
    b = np.dot(n, points.transpose())

    iSelect = np.where(b < a)
    pointsBelow = points[iSelect, :].squeeze()

    return pointsBelow

def findPointsInAxisRange(points, lim, axis = 0):
    '''find points within axis limits
       lim: tuple of minimum and maximum value
    '''
    
    iSelect = np.all(
        [lim[0] < points[:,axis],
        points[:,axis] < lim[1]],
        axis = 0
    )
    
    pointsInRange = points[iSelect]
    return pointsInRange


def findPointsInRange(points, n, a, tol):
    '''find points in a plane defined by Hessian Form n * x = a
       n: normal vector
       a: distance from origin
       tol: distance tolerance
    '''
    
    b = np.dot(n, points.transpose())

    isInRange = np.abs(a - b) < tol
    iSelect = np.where(isInRange)
    pointsInRange = points[iSelect]
    
    return pointsInRange