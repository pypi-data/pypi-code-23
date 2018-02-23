# -*- coding: utf-8 -*-
"""
Created on Thu Jun 04 07:57:15 2015

@author: twagner
"""

### imports ###################################################################
import numpy as np
import scipy.optimize

###############################################################################
class CircleFit:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.optimize()

    def optimize(self):
        
        x_m = np.mean(self.x)
        y_m = np.mean(self.y)

        center_estimate = x_m, y_m
        
        center, ier = scipy.optimize.leastsq(
                self.f,
                center_estimate,
                Dfun=self.Df,
                col_deriv = True)
        
        self.xc, self.yc = center
        Ri = self.calcRadius(*center)
        self.R = Ri.mean()
        self.residue = sum((Ri - self.R)**2)

    ###########################################################################
    def calcRadius(self, xc, yc):
        """ calculate the distance of each data points from the
            center (xc, yc)
        """
        return np.sqrt((self.x - xc)**2 + (self.y - yc)**2)

    def f(self, c):
        """ calculate the algebraic distance between the 2D points and the mean
            circle centered at c=(xc, yc)
        """
        
        Ri = self.calcRadius(*c)
        return Ri - Ri.mean()

    def Df(self, c):
        """ Jacobian of f_2b
            The axis corresponding to derivatives must be coherent with the
            col_deriv option of leastsq
        """
        
        xc, yc = c
        Nx = self.x.size
        
        df2b_dc    = np.empty((len(c), Nx))
    
        Ri = self.calcRadius(xc, yc)
        df2b_dc[0] = (xc - self.x) / Ri                   # dR/dxc
        df2b_dc[1] = (yc - self.y) / Ri                   # dR/dyc
        df2b_dc    = df2b_dc - df2b_dc.mean(axis = 1)[:, np.newaxis]
    
        return df2b_dc
