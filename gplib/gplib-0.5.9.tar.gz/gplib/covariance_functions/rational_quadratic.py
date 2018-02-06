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


class RationalQuadratic(StationaryFunction):
    """

    """
    def __init__(self, data, is_ard):
        hyperparams = [
            OptimizableParameter(
                'output_variance2', LogTransformation,
                default_value=np.std(data['Y']),
                min_value=np.exp(-10), max_value=np.exp(10)
            ),
            OptimizableParameter(
                'alpha', LogTransformation,
                default_value=2.0,
                min_value=np.exp(-10), max_value=np.exp(10)
            )
        ]

        super(RationalQuadratic, self).__init__(data, is_ard, hyperparams)

    def stationary_function(self, sq_dist):
        """
        It applies the Rational Quadratic kernel function
        element-wise to the distance matrix.

        .. math::
            k_{RQ}(r)=(1+\dfrac{1}{2*\alpha}(\dfrac{r}{l})^2)^{-\alpha}

        :param sq_dist: Distance matrix
        :param hyperparams:
        :return: Result matrix with kernel function applied element-wise.
        """
        return np.power(
                1.0 + (1.0/(2.0*self.get_param_value('alpha'))) * sq_dist,
                -self.get_param_value('alpha')
            ) * self.get_param_value('output_variance2')

    def dkr_dx(self, sq_dist, dr_dx):
        """
        Measures gradient of the kernel function in X.

        :param sq_dist: Square distance
        :param dr_dx:
        :return: 3D array with the gradient of the kernel function in every
         dimension of X.
        """
        #TODO test this
        return -0.5 * dr_dx * self.get_param_value('output_variance2') *\
            np.power(
                (1.0 + (1.0/(2.0*self.get_param_value('alpha'))) * sq_dist),
                -self.get_param_value('alpha')-1.0
            )[:, :, np.newaxis]


    def dkr_dtheta(self, sq_dist, dr_dtheta):
        """
        Measures gradient of the kernel function in the
        hyper-parameter space.

        :param sq_dist: Square distance
        :param dr_dtheta:
        :return: 3D array with the gradient of the kernel function in every
         dimension the length-scale hyper-parameter space.
        """
        division = (1.0 / (2.0 * self.get_param_value('alpha'))) * sq_dist

        k = np.power(
            1.0 + division,
            -self.get_param_value('alpha')
        )

        return k, \
            self.get_param_value('output_variance2') * k * \
               ((division / (division + 1.0)) - np.log(division + 1.0)), \
            -0.5 * dr_dtheta * self.get_param_value('output_variance2') *\
               np.power(
                   1.0 + division,
                   -self.get_param_value('alpha')-1.0
               )[:, :, np.newaxis]
