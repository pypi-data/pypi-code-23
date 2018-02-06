# -*- coding: utf-8 -*-

### imports ###################################################################
import matplotlib.pyplot as plt
import numpy as np

###############################################################################
r = 1. # circle radius
x_m = 100.
y_m = 0.
m = np.array((x_m, y_m))
r_m_2 = x_m**2 + y_m**2

N = 4 * 361

alpha_deg =  np.linspace(-1., 1., num=N)
alpha_array = np.radians(alpha_deg)

a = np.zeros(N)

for i, alpha in enumerate(alpha_array):
    nx = np.cos(alpha)
    ny = np.sin(alpha)
    n = np.array((nx, ny))
    
    nm = np.dot(n, m)
    
    aa = nm**2 + r**2 - r_m_2
    
    if aa >= 0:
        a[i] = nm - np.sqrt(aa)
    else:
        a[i] = np.NaN

plt.plot(alpha_deg, a, 'o')
    