#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/2/6 15:26
# @Author  : Mamba
# @Site    : 
# @File    : test1.py


from Ball.utilize import *

x = [np.random.normal(0, 1, a) for a in [40, 50, 60]]
if type(x) is list:
    size = []
    for i in range(0, len(x)):
        size.append(x[i].shape[0])
        x[i] = np.matrix(x[i])
        x[i] = np.transpose(x[i])
    a = x[0]
    for i in range(1, len(x)):
        a = np.row_stack((a, x[i]))
    x = a
xy = x
dst = False

# x = [np.random.normal(0, 1, a) for a in [40, 50, 60]]
# size = []
# for i in range(0, len(x)):
#     size.append(x[i].shape[0])
#     x[i] = np.matrix(x[i])
#     x[i] = np.transpose(x[i])
# #print(len(np.row_stack((x[0],x[1]))))
# a= x[0]
# for i in range(1, len(x)):
#     a = np.row_stack((a, x[i]))
# x = a
# x1 = np.matrix(x)
# p = len(x1[0])
# print(p)
#
# # from sklearn.metrics.pairwise import euclidean_distances
# # sigma = [[1, 0], [0, 1]]
# # x = np.random.multivariate_normal(mean=[0, 0], cov=sigma, size=50)
# # y = np.random.multivariate_normal(mean=[1, 1], cov=sigma, size=50)
# # x = np.row_stack((x, y))
# # dx = euclidean_distances(x, x)
# # size = [50, 50]
# # x = get_matrixed_x(dx, y)
# # xy = np.array(x.flatten())
# # xy = x.flatten()
# #
# #
# # print(xy)
