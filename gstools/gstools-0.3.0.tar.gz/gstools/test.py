#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function

import numpy as np
import matplotlib.pyplot as pt
import seaborn
from gstools.field import SRF

import variogram


def unstructured_2d(x, y, f, bins):
    variogram = np.zeros(len(bins)-1, dtype=np.double)
    counts = np.zeros_like(variogram, dtype=int)
    for i in range(len(bins)-1):
        for j in range(len(x)-1):
            for k in range(j+1, len(x)):
                diff = np.sqrt((x[k] - x[j])**2 + (y[k] - y[j])**2)
                if diff >= bins[i] and diff < bins[i+1]:
                    counts[i] += 1
                    variogram[i] += (f[k] - f[j])**2
    #avoid division by zero
    counts[counts == 0] = 1
    variogram /= (2. * counts)
    return variogram

def unstructured_1d(x, f, bins):
    vario = np.zeros(len(bins)-1, dtype=np.double)
    counts = np.zeros_like(vario, dtype=int)
    for i in range(len(bins)-1):
        for j in range(len(x)-1):
            for k in range(j+1, len(x)):
                diff = x[k] - x[j]
                if diff >= bins[i] and diff < bins[i+1]:
                    counts[i] += 1
                    vario[i] += (f[k] - f[j])**2
    counts[counts == 0] = 1
    vario /= (2. * counts)
    return vario


def time_python_cython(time_python=False):
    import timeit

    x = np.array(np.random.randint(0., 5., 3000), dtype=np.double)
    y = np.array(np.random.randint(0., 5., 3000), dtype=np.double)

    bins = np.array((0, .2, .5, 1, 2, 3, 4))

    cov_model = {
                 'dim': 2,
                 'mean': 0.,
                 'var': .1,
                 'len_scale': 4.5,
                 'model': 'gau',
                 }
    
    srf = SRF(**cov_model)
    field = srf(x, y, seed=47345653)

    start_time = timeit.default_timer()
    vario_c = variogram.unstructured(field, bins, x, y)
    elapsed_c = timeit.default_timer() - start_time

    print('cython elapsed time = {}'.format(elapsed_c))

    if time_python:
        start_time = timeit.default_timer()
        vario = unstructured_2d(x, y, field, bins)
        elapsed = timeit.default_timer() - start_time
        print('python elapsed time = {}'.format(elapsed))


def gaussian_variogram(x, var, len_scale):
    return var * (1. - np.exp(-x**2 / len_scale**2))


if __name__ == '__main__':
    time_python_cython(False)

    x_max = 40.
    x_c = np.linspace(0., x_max, 40)
    y_c = np.linspace(0., x_max, 40)
    x, y = np.meshgrid(x_c, y_c)
    x = np.reshape(x, len(x_c)*len(y_c))
    y = np.reshape(y, len(x_c)*len(y_c))

    field = x * y

    bins = np.arange(0., x_max/2., .5)

    vario_c = variogram.unstructured(field, bins, x, y)

    pt.plot(bins[:-1], vario_c)
    pt.show()

    #x_max = 40.
    #x_c = np.linspace(0., x_max, 100)
    #y_c = np.linspace(0., x_max, 100)
    #x, y = np.meshgrid(x_c, y_c)
    #x = np.reshape(x, len(x_c)*len(y_c))
    #y = np.reshape(y, len(x_c)*len(y_c))

    #bins = np.arange(0., x_max/2., .5)

    #cov_model = {
    #             'dim': 2,
    #             'mean': 0.,
    #             'var': .1,
    #             'len_scale': 4.5,
    #             'model': 'gau',
    #             }
    #srf = SRF(**cov_model)
    #field = srf(x, y, seed=47345653)

    #vario_c = variogram.unstructured(field, bins, x, y)
    #vario_t = gaussian_variogram(bins[:-1], cov_model['var'], cov_model['len_scale'])

    #pt.plot(bins[:-1], vario_c)
    #pt.plot(bins[:-1], vario_t, linestyle='--')
    #pt.savefig('var.png', dpi=300)
    #pt.show()
