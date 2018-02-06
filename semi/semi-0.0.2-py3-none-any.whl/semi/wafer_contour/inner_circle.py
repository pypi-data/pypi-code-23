# -*- coding: utf-8 -*-

### imports ###################################################################
import matplotlib.pyplot as plt
import numpy as np

###############################################################################
class InnerCircle:
    def __init__(self, r=78, **kwargs):
        ### wafer radius
        self.r = r

        ### wafer offset
        self.alpha_off_deg = 0.
        self.r_off = 0.
        
        for key, value in kwargs.items():
            if key == 'alpha_off':
                self.alpha_off = value
            elif key == 'r_off':
                self.r_off = value

        # self.alpha_off = np.radians(self.alpha_off_deg)


    def contour(self, **kwargs):
        alpha_0_deg = -180
        alpha_1_deg = 180        

        res = np.radians(1)
        
        for key, value in kwargs.items():
            if key == 'res_deg':
                res = value
        
        N = int(np.ceil((alpha_1_deg - alpha_0_deg) / res))
        
        alpha_deg =  np.linspace(alpha_0_deg, alpha_1_deg, num=N)
        
        alpha = np.radians(alpha_deg)
        y = self.r - self.r_off * np.cos(alpha - self.alpha_off)

        return (alpha_deg, y)


###############################################################################        
if __name__ == '__main__':    
    ### wafer radius
    r = 156.
    
    ### wafer offset
    r_off = 1.
    alpha_off_deg = 45.
    
    inner_circle = InnerCircle(alpha_off_deg=alpha_off_deg, r_off=r_off)
    alpha_deg, y = inner_circle.contour()
    
    plt.close('all')
    plt.plot(alpha_deg, y - r, '.')




