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


class Exponential(StationaryFunction):
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

        super(Exponential, self).__init__(data, is_ard, hyperparams)

    def stationary_function(self, sq_dist):
        """
        It applies the exponential kernel function
        element-wise to the distance matrix.

        .. math::
            k_{E}(r) = \exp (-\dfrac{r}{l})

        :param sq_dist: Distance matrix
        :param hyperparams:
        :return: Result matrix with kernel function applied element-wise.
        """
        dist = np.sqrt(sq_dist)
        return np.exp(-dist) * self.get_param_value('output_variance2')

    def dkr_dx(self, sq_dist, dr_dx):
        """
        Measures gradient of the kernel function in X.

        :param sq_dist: Square distance
        :param dr_dx:
        :return: 3D array with the gradient of the kernel function in every
         dimension of X.
        """
        sq_power = sq_dist.copy()
        sq_power[sq_power != 0.0] = np.power(sq_power[sq_power != 0.0], -0.5)
        result = -0.5 * sq_power[:, :, np.newaxis] * \
                 np.exp(-np.power(sq_dist, 0.5))[:, :, np.newaxis] * dr_dx
        return result * self.get_param_value('output_variance2')

    def dkr_dtheta(self, sq_dist, dr_dtheta):
        """
        Measures gradient of the kernel function in the
        hyper-parameter space.

        :param sq_dist: Square distance
        :param dr_dtheta:
        :return: 3D array with the gradient of the kernel function in every
         dimension the length-scale hyper-parameter space.
        """
        dist = np.sqrt(sq_dist)
        sq_power = sq_dist.copy()
        sq_power[sq_power != 0.0] = np.power(sq_power[sq_power != 0.0], -0.5)
        result = -0.5 * sq_power[:, :, np.newaxis] * \
                 np.exp(-np.power(sq_dist, 0.5))[:, :, np.newaxis] * dr_dtheta
        return np.exp(-dist), result * self.get_param_value('output_variance2')
