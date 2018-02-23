# -*- coding: utf-8 -*-

import numpy as np

def fit_line(x, y):
    dim = 2
    N = len(x)

    x0 = np.ones(N)
    
    A = np.vstack((x0, x, y)).T
    
    (m, p) = A.shape
    
    m = np.min(A.shape)
    
    R = np.linalg.qr(A, mode='r')
    R_sub = R[p-dim:,p-dim:p]
    
    U, S, Vh = np.linalg.svd(R_sub)
    
    n = Vh[1,:]
    
    a = np.dot(R[0, 1:], n) / R[0, 0]
    
    sign = np.sign(a)
    a *= sign
    n *= sign

    return n, a
