#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/2/6 18:13
# @Author  : Mamba
# @Site    : 
# @File    : test3.py

import numpy as np

from Ball.bd_test import bd_test

np.random.seed(7654567)
# x = np.random.normal(0, 1, 100).reshape(50, 2)
# y = np.random.normal(3, 1, 100).reshape(50, 2)
# a = bd_test(x=x, y=y)
# n = 90
# a = bd_test(np.random.normal(0, 1, n), size=np.array([40, 50]))
# x = [np.random.normal(0, 1, num) for num in [40, 50]]
# a = bd_test(x)
from sklearn.metrics.pairwise import euclidean_distances
sigma = [[1, 0], [0, 1]]
x = np.random.multivariate_normal(mean=[0, 0], cov=sigma, size=50)
y = np.random.multivariate_normal(mean=[1, 1], cov=sigma, size=50)
x = np.row_stack((x, y))
dx = euclidean_distances(x, x)
data_size = [50, 50]
a = bd_test(x=dx, size=data_size, dst=True)
print(a)
