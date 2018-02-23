# -*- coding: utf-8 -*-

### imports ###################################################################
import numpy as np

###############################################################################
class Points2D(object):
    def __init__(self, x, y):
        self.x = np.array(x)
        self.y = np.array(y)

    @property
    def xy(self):
        return np.vstack((self.x, self.y)).T
       
    def getProfile(self):
        return self.x, self.y

    def rotate(self, alpha):
        sin_alpha = np.sin(alpha)
        cos_alpha = np.cos(alpha)

        x = self.x * cos_alpha - self.y * sin_alpha
        y = self.x * sin_alpha + self.y * cos_alpha
        
        return Points2D(x, y)