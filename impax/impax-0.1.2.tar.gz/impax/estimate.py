from __future__ import absolute_import

import pandas as pd
import numpy as np
import csv
from scipy.stats import multivariate_normal

import warnings


def read_csvv(csvv_path):
    '''
    Returns the estimator object from a CSVV file

    Parameters
    ----------
    path: str_or_buffer
        path to csvv file

    Returns
    -------
    estimator : MultivariateNormalEstimator
        :py:class:`Gamma` object with median and VCV matrix indexed by
        prednames, covarnames, and outcomes

    '''

    data = {}

    with open(csvv_path, 'r') as fp:
        reader = csv.reader(fp)

        for row in reader:
            if row[0] == 'gamma':
                data['gamma'] = np.array([float(i) for i in next(reader)])
            if row[0] == 'gammavcv':
                data['gammavcv'] = np.array([float(i) for i in next(reader)])
            if row[0] == 'residvcv':
                data['residvcv'] = np.array([float(i) for i in next(reader)])
            if row[0] == 'prednames':
                data['prednames'] = [i.strip() for i in next(reader)]
            if row[0] == 'covarnames':
                data['covarnames'] = [i.strip() for i in next(reader)]
            if row[0] == 'outcome':
                data['outcome'] = [cv.strip() for cv in next(reader)]

    index = pd.MultiIndex.from_tuples(
        list(zip(data['outcome'], data['prednames'], data['covarnames'])),
        names=['outcome', 'prednames', 'covarnames'])

    g = MultivariateNormalEstimator(data['gamma'], data['gammavcv'], index)

    return g


def get_gammas(*args, **kwargs):
    warnings.warn(
        'get_gammas has been deprecated, and has been replaced with read_csvv',
        DeprecationWarning)

    return read_csvv(*args, **kwargs)


class MultivariateNormalEstimator(object):
    '''
    Stores a median and residual VCV matrix for multidimensional variables with
    named indices and provides multivariate sampling and statistical analysis
    functions

    Parameters
    ----------
    coefficients: array
        length :math:`(m_1*m_2*\cdots*m_n)` 1-d :py:class:`numpy.ndarray` with
        regression coefficients

    vcv: array
        :math:`(m_1*m_2*\cdots*m_n) x (m_1*m_2*\cdots*m_n)`
        :py:class:`numpy.ndarray` with variance-covariance matrix for
        multivariate distribution

    index: Index
        :py:class:`~pandas.Index` or :math:`(m_1*m_2*\cdots*m_n)` 1-d
        :py:class:`~pandas.MultiIndex` describing the multivariate space

    '''

    def __init__(self, coefficients, vcv, index):
        self.coefficients = coefficients
        self.vcv = vcv
        self.index = index

    def median(self):
        '''
        Returns the median values (regression coefficients)

        Returns
        -------
        median : DataArray
            :py:class:`~xarray.DataArray` of coefficients
        '''

        return pd.Series(self.coefficients, index=self.index).to_xarray()

    def sample(self, seed=None):
        '''
        Sample from the multivariate normal distribution

        Takes a draw from a multivariate distribution and returns
        an :py:class:`xarray.DataArray` of parameter estimates.

        Returns
        ----------
        draw : DataArray
            :py:class:`~xarray.DataArray` of parameter estimates drawn from the
            multivariate normal

        '''
        if seed is not None:
            warnings.warn((
                'Sampling with a seed has been deprecated. In future releases,'
                ' this will be up to the user.'),
                DeprecationWarning)
            np.random.seed(seed)

        return pd.Series(
            multivariate_normal.rvs(self.coefficients, self.vcv),
            index=self.index).to_xarray()
