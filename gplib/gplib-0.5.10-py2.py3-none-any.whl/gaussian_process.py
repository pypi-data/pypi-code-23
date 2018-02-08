# -*- coding: utf-8 -*-
#
#    Copyright 2018 Ibai Roman
#
#    This file is part of GPlib.
#
#    GPlib is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    GPlib is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with GPlib. If not, see <http://www.gnu.org/licenses/>.

import copy

import numpy as np
import scipy.linalg

from .parameters import WithParameters
from .covariance_functions.posterior import Posterior as PosteriorCov
from .mean_functions.posterior import Posterior as PosteriorMean


class GaussianProcess(WithParameters):
    """
    GPlib module for Gaussian Process
    """
    def __init__(self,
                 mean_function,
                 covariance_function,
                 likelihood_function,
                 inference_method,
                 fitting_method = None):
        self.mean_function = mean_function
        self.covariance_function = covariance_function
        self.likelihood_function = likelihood_function
        self.inference_method = inference_method
        self.fitting_method = fitting_method

        self.likelihood_function.set_gp(self)
        self.inference_method.set_gp(self)
        if self.fitting_method:
            self.fitting_method.set_gp(self)

        super(GaussianProcess, self).__init__([
            mean_function, covariance_function, likelihood_function
        ])

    def get_posterior(self, data):
        """

        :param data:
        :type data:
        :return:
        :rtype:
        """
        likelihood_function = copy.copy(self.likelihood_function)
        inference_method = copy.copy(self.inference_method)
        fitting_method = copy.copy(self.fitting_method)

        data_copy = copy.deepcopy(data)

        return GaussianProcess(
            PosteriorMean(
                self.mean_function.get_hyperparams(),
                self,
                data_copy
            ),
            PosteriorCov(
                self.covariance_function.get_hyperparams(),
                self,
                data_copy
            ),
            likelihood_function,
            inference_method,
            fitting_method
        )

    def sample(self, test_points, n_samples=10):
        """ Sample the prior of the GP """
        mean = self.mean_function.marginalize_mean(
            test_points)
        covariance = self.covariance_function.marginalize_covariance(
            test_points)

        l_matrix = self.safe_chol(covariance)
        rnd = np.random.randn(test_points.shape[0], n_samples)

        return mean.reshape(-1, 1) + np.dot(l_matrix, rnd)

    @staticmethod
    def safe_chol(k_matrix):
        """ Compute cholesky decomposition """
        assert not np.isnan(k_matrix).any(), "NaN values in cov matrix"
        assert not np.isinf(k_matrix).any(), "Inf values in cov matrix"

        solved = False
        l_matrix = None
        jitter = 0.0
        while not solved:
            k_corrected = np.ascontiguousarray(k_matrix +
                                               jitter*np.eye(k_matrix.shape[0]))
            l_matrix, error = scipy.linalg.lapack.dpotrf(k_corrected, lower=1)
            if error == 0:
                solved = True
            elif jitter == 0.0:
                jitter = 1e-20
            elif jitter < 1e-10:
                jitter *= 10
            else:
                raise np.linalg.linalg.LinAlgError(
                    'Kernel function is not positive semi-definite')

        if np.isnan(l_matrix).any() or np.isinf(l_matrix).any():
            raise np.linalg.linalg.LinAlgError(
                'NaNs or Infs during cholesky descomposition')
        return l_matrix

    # TODO gradients needed
