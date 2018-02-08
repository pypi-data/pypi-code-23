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

from .covariance_function import CovarianceFunction
from ..parameters import OptimizableParameter
from ..transformations import LogTransformation


class Periodic(CovarianceFunction):
    """

    """
    def __init__(self, kernel, data, is_ard):
        default_period = 1.0
        if is_ard:
            dims = data['X'].shape[1]
            default_period = np.ones(dims).tolist()

        self.kernel = kernel

        super(Periodic, self).__init__([
            kernel,
            OptimizableParameter(
                'period', LogTransformation,
                default_value=default_period,
                min_value=np.exp(-1), max_value=np.exp(5)
            )
        ])

    def covariance(self, mat_a, mat_b=None, only_diagonal=False):
        """
        Measures the distance matrix between solutions of A and B, and
        applies the kernel function element-wise to the distance matrix.

        :param mat_a: List of solutions in lines and dimensions in columns.
        :type mat_a:
        :param mat_b: List of solutions in lines and dimensions in columns.
        :type mat_b:
        :param only_diagonal:
        :type only_diagonal:
        :return: Result matrix with kernel function applied element-wise.
        :rtype:
        """

        a_param = np.divide(2.0 * np.pi, self.get_param_value('period'))

        exp_mat_b=None
        if mat_b is not None:
            exp_mat_b = np.hstack((
                np.sin(a_param * mat_b),
                np.cos(a_param * mat_b)
            ))

        return self.kernel.marginalize_covariance(
            np.hstack((
                np.sin(a_param * mat_a),
                np.cos(a_param * mat_a)
            )),
            mat_b=exp_mat_b,
            only_diagonal=only_diagonal,
            dk_dx_needed=False,
            dk_dtheta_needed=False
        )

    def dk_dx(self, mat_a, mat_b=None):
        """
        Measures gradient of the distance between solutions of A and B in X.

        :param mat_a: List of solutions in lines and dimensions in columns.
        :param mat_b: List of solutions in lines and dimensions in columns.
        :return: 3D array with the gradient in every dimension of X.
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def dk_dtheta(self, mat_a, mat_b=None):
        """
        Measures gradient of the distance between solutions of A and B in the
        hyper-parameter space.

        :param mat_a: List of solutions in lines and dimensions in columns.
        :param mat_b: List of solutions in lines and dimensions in columns.
        :return: 3D array with the gradient in every
         dimension the length-scale hyper-parameter space.
        """

        raise NotImplementedError("Not Implemented. This is an interface.")
