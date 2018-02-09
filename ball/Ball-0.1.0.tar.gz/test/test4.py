#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/2/9 19:34
# @Author  : Mamba
# @Site    : 
# @File    : test4.py

import numpy as np
from sklearn.metrics.pairwise import euclidean_distances
from Ball import bd_test, bd

x = np.random.normal(0, 1, 50)
y = np.random.normal(1, 1, 50)
print(bd(x=x, y=y))
print(bd_test(x=x, y=y))

x = np.random.normal(0, 1, 100).reshape(50, 2)
y = np.random.normal(3, 1, 100).reshape(50, 2)
print(bd(x=x, y=y))
print(bd_test(x=x, y=y))

n = 90
x = np.random.normal(0, 1, n)
print(bd(x, size=np.array([40, 50])))
print(bd_test(x, size=np.array([40, 50])))

x = [np.random.normal(0, 1, num) for num in [40, 50]]
print(bd(x))
print(bd_test(x))

sigma = [[1, 0], [0, 1]]
x = np.random.multivariate_normal(mean=[0, 0], cov=sigma, size=50)
y = np.random.multivariate_normal(mean=[1, 1], cov=sigma, size=50)
x = np.row_stack((x, y))
dx = euclidean_distances(x, x)
data_size = [50, 50]
print(bd(x=dx, size=data_size, dst=True))
print(bd_test(x=dx, size=data_size, dst=True))
