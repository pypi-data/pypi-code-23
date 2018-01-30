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

from ..cache import CachedMethod
from ..parameters import WithParameters


class CovarianceFunction(WithParameters):
    """

    """
    def __init__(self, hyperparams):

        self.cache = {
            'hash': 0,
            'result': None
        }

        super(CovarianceFunction, self).__init__(hyperparams)

    def __copy__(self):

        copyed_object = self.__class__()

        copyed_object.set_hyperparams(self.get_hyperparams())

        return copyed_object

    @CachedMethod(lambda this, mat_a, mat_b=None,
                  only_diagonal=False,
                  dk_dx_needed=False,
                  dk_dtheta_needed=False:
        hash((
            hash(mat_a.tostring()),
            hash(mat_b if mat_b is None else mat_b.tostring()),
            hash(only_diagonal),
            hash(dk_dx_needed),
            hash(dk_dtheta_needed),
            hash(
                this.prior_data['X'].tostring()
                if hasattr(this, 'prior_data') else
                None
            ),
            hash(
                this.prior_data['Y'].tostring()
                if hasattr(this, 'prior_data') else
                None
            ),
            hash(
                tuple(this.prior_gp.get_param_values())
                if hasattr(this, 'prior_gp') else
                tuple(this.get_param_values())
            )
        ))
    )
    def marginalize_covariance(self, mat_a, mat_b=None,
                               only_diagonal=False,
                               dk_dx_needed=False,
                               dk_dtheta_needed=False):
        """
        Measures the distance matrix between solutions of A and B, and
        applies the kernel function element-wise to the distance matrix.

        :param mat_a: List of solutions in lines and dimensions in columns.
        :type mat_a:
        :param mat_b: List of solutions in lines and dimensions in columns.
        :type mat_b:
        :param only_diagonal:
        :type only_diagonal:
        :param dk_dx_needed: It should be true if the derivative in x is needed.
        :type dk_dx_needed:
        :param dk_dtheta_needed: It should be true if the derivative in
            theta is needed.
        :type dk_dtheta_needed:
        :return: Result matrix with kernel function applied element-wise.
        :rtype:
        """
        covariance = self.covariance(
            mat_a, mat_b=mat_b, only_diagonal=only_diagonal)

        result = (covariance, )

        if dk_dx_needed:
            dk_dx = self.dk_dx(
                mat_a, mat_b=mat_b)
            result += (dk_dx, )

        if dk_dtheta_needed:
            dk_dtheta = self.dk_dtheta(
                mat_a, mat_b=mat_b)
            result += (dk_dtheta, )

        if len(result) == 1:
            result = result[0]

        return result

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

        raise NotImplementedError("Not Implemented. This is an interface.")

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
