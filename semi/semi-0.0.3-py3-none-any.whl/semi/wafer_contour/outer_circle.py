# -*- coding: utf-8 -*-

### imports ###################################################################
import matplotlib.pyplot as plt
import numpy as np

###############################################################################
class OuterCircle:
    def __init__(self, **kwargs):
        # self.M = np.array(M)

        for key, value in kwargs.items():
            if key == 'M':
                self.M = value
            if key == 'r':
                # circle radius
                self.r = value
            elif key == 'x0':
                self.x0 = value
            elif key == 'x1':
                self.x1 = value


    def contour(self, **kwargs):
        # alpha_0_deg = -180
        # alpha_1_deg = 180

        res = np.radians(1)
        
        for key, value in kwargs.items():
            if key == 'res_deg':
                res = value

        alpha_0 = np.arctan2(self.x0[1], self.x0[0])
        alpha_1 = np.arctan2(self.x1[1], self.x1[0])

        alpha_0_deg = np.rad2deg(alpha_0)
        alpha_1_deg = np.rad2deg(alpha_1)               

        print(alpha_0_deg)
        print(alpha_1_deg)
        
        N = int(np.ceil((alpha_1_deg - alpha_0_deg) / res))
        
        alpha_deg =  np.linspace(alpha_0_deg, alpha_1_deg, num=N)
        alpha_array = np.radians(alpha_deg)
        
        r_m_2 = np.dot(self.M, self.M) # (distance of mid point)**2
        a = np.zeros(N)
        
        for i, alpha in enumerate(alpha_array):
            nx = np.cos(alpha)
            ny = np.sin(alpha)
            n = np.array((nx, ny))
            
            nm = np.dot(n, self.M)
            
            aa = nm**2 + self.r**2 - r_m_2
            
            if aa >= 0:
                a[i] = nm - np.sqrt(aa)
            else:
                a[i] = np.NaN

        return alpha_deg, a

###############################################################################
if __name__ == '__main__':
    # circle mid point
    x_m = 78.
    y_m = 10.
    M = (x_m, y_m)

    r = 1. # circle radius
    outerCircle = OuterCircle(r=r, M=M)
    alpha_deg, a = outerCircle.contour()
    
    plt.plot(alpha_deg, a, 'o')
        