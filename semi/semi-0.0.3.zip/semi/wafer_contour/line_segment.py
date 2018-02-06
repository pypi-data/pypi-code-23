# -*- coding: utf-8 -*-

### imports ###################################################################
import numpy as np

###############################################################################
class LineSegment(object):
    def __init__(self, **kwargs):
        
        ### wafer offset
        self.alpha_off_deg = 0.
        self.r_off = 0.

        # line distance
        self.a = 1.

        # line normal
        self._n = None

        # self.x0 = self.a * self.n - self.p
        # self.x1 = self.a * self.n + self.p
        
        self.x0 = None
        self.x1 = None

        for key, value in kwargs.items():
            if key == 'a':
                self.a = value
            elif key == 'normal':
                nx, ny = value
                self.n = value
            elif key == 'r_off':
                self.r_off = value
            elif key == 'x0':
                self.x0 = value
            elif key == 'x1':
                self.x1 = value

        if self.x0 is not None and self.x1 is not None and self._n is None:
            dx = self.x1 - self.x0
            self.p = dx / np.linalg.norm(dx)

            nx = self.p[1]
            ny = -self.p[0]
            self._n = np.array((nx, ny))
            self.alpha_normal = np.arctan2(ny, nx)
            
            self.a = np.dot(self.n, self.x0)
            
            print('n:', self.n, 'a:', self.a)


    @property
    def n(self):
        return self._n

    @n.setter
    def n(self, value):
        self._n = np.array(value)

        nx = self._n[0]
        ny = self._n[1]
        
        self.p = np.array((-ny, nx))

        self.alpha_normal = np.arctan2(ny, nx)

        
    def contour(self, **kwargs):
        res = np.radians(1)
        
        for key, value in kwargs.items():
            if key == 'res_deg':
                res = np.radians(value)
        
        alpha_0 = np.arctan2(self.x0[1], self.x0[0])
        alpha_1 = np.arctan2(self.x1[1], self.x1[0])

        if alpha_1 < alpha_0 and alpha_1 < 0 and alpha_0 > 0:
            alpha_1 += 2 * np.pi

        N = int(np.ceil(np.abs(alpha_1 - alpha_0) / res))
        
        alpha = np.linspace(alpha_0, alpha_1, N)
        alpha_deg = np.rad2deg(alpha)
        alpha_deg[alpha_deg > 180.] -= 360
        
        y = self.a / np.cos(alpha - self.alpha_normal)
    
        return (alpha_deg, y)



    
