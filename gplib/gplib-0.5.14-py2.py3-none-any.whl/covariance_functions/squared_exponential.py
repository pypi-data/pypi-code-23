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

import numpy as np

from .stationary_function import StationaryFunction
from ..parameters import OptimizableParameter
from ..transformations import LogTransformation


class SquaredExponential(StationaryFunction):
    """

    """
    def __init__(self, data, is_ard):
        hyperparams = [
            OptimizableParameter(
                'output_variance2', LogTransformation,
                default_value=np.std(data['Y']),
                min_value=np.exp(-10), max_value=np.exp(10)
            )
        ]

        super(SquaredExponential, self).__init__(data, is_ard, hyperparams)

    def stationary_function(self, sq_dist):
        """
        It applies the Squared Exponential kernel function
        element-wise to the distance matrix.

        .. math::
            k_{SE}(r)=exp (-\dfrac{1}{2}(\dfrac{r}{l})^2)

        :param sq_dist: Distance matrix
        :param hyperparams:
        :return: Result matrix with kernel function applied element-wise.
        """
        return np.exp(-0.5 * sq_dist) * self.get_param_value('output_variance2')

    def dkr_dx(self, sq_dist, dr_dx):
        """
        Measures gradient of the kernel function in X.

        :param sq_dist: Square distance
        :param dr_dx:
        :return: 3D array with the gradient of the kernel function in every
         dimension of X.
        """
        return -0.5 * np.exp(-0.5 * sq_dist)[:, :, np.newaxis] * dr_dx * \
               self.get_param_value('output_variance2')

    def dkr_dtheta(self, sq_dist, dr_dtheta):
        """
        Measures gradient of the kernel function in the
        hyper-parameter space.

        :param sq_dist: Square distance
        :param dr_dtheta:
        :return: 3D array with the gradient of the kernel function in every
         dimension the length-scale hyper-parameter space.
        """
        return np.exp(-0.5 * sq_dist), \
               -0.5 * np.exp(-0.5 * sq_dist)[:, :, np.newaxis] * dr_dtheta * \
               self.get_param_value('output_variance2')
