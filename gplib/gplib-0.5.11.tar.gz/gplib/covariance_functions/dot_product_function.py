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
from ..transformations import NoneTransformation


class DotProductFunction(CovarianceFunction):
    """

    """
    def __init__(self, data, is_ard, hyperparams):
        default_lengthscale = 1.0
        default_shift = 1.0
        if is_ard:
            dims = data['X'].shape[1]
            default_lengthscale = np.ones(dims).tolist()
            default_shift = np.ones(dims).tolist()

        hyperparams.append(OptimizableParameter(
            'lengthscale', LogTransformation,
            default_value=default_lengthscale,
            min_value=np.exp(-10), max_value=np.exp(10)
        ))

        hyperparams.append(OptimizableParameter(
            'shift', NoneTransformation,
            default_value=default_shift,
            min_value=np.exp(-10), max_value=np.exp(10)
        ))

        super(DotProductFunction, self).__init__(hyperparams)

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

        dot_product = self.dot_product(
            mat_a, mat_b=mat_b,
            only_diagonal=only_diagonal
        )

        covariance = self.dot_product_function(dot_product)

        return covariance

    def dot_product(self, mat_a, mat_b=None, only_diagonal=False):
        """
        Dot product of A and B.

        :param mat_a: List of solutions in lines and dimensions in columns.
        :type mat_a:
        :param mat_b: List of solutions in lines and dimensions in columns.
        :type mat_b:
        :param only_diagonal:
        :type only_diagonal:
        :return: dot product between solutions of A and B.
        :rtype:
        """
        mat_a = (mat_a - self.get_param_value('shift')) / \
            self.get_param_value('lengthscale')


        if mat_b is None:
            if only_diagonal:
                return np.sum(np.square(mat_a), axis=1)[:, None]
            return np.dot(mat_a, mat_a.T)

        mat_b = (mat_b - self.get_param_value('shift')) / \
            self.get_param_value('lengthscale')

        return np.dot(mat_a, mat_b.T)

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

    def dot_product_function(self, dot_product):
        """

        :param dot_product:
        :type dot_product:
        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")
