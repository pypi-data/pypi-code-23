# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 17:13:16 2018

@author: 99493
"""

from test import cball

N = 1000
b = cball.doubleArray(N)
for i in range(N):
    b[i] = float(i)/10.0

n1 = N / 2
n1 = int(n1)
n2 = N - n1
print(cball.bd_stat(b, n1, n2, 0, 0))

bd = cball.doubleArray(1)
permuted_bd = cball.doubleArray(100)
R = 100
cball.bd_test(bd, permuted_bd, b, n1, n2, 1, 0, R, 0)
print(bd[0])
print(permuted_bd[0])
print(permuted_bd[99])
print(permuted_bd[100])

