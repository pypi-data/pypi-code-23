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

class MeanFunction(WithParameters):
    """

    """
    def __init__(self, hyperparams):

        self.cache = {
            'hash': 0,
            'result': None
        }

        super(MeanFunction, self).__init__(hyperparams)

    def __copy__(self):

        copyed_object = self.__class__()

        copyed_object.set_hyperparams(self.get_hyperparams())

        return copyed_object

    @CachedMethod(lambda self, x,
                  dk_dx_needed=False,
                  dk_dtheta_needed=False:
        hash((
            hash(x.tostring()),
            hash(dk_dx_needed),
            hash(dk_dtheta_needed),
            hash(
                self.prior_data['X'].tostring()
                if hasattr(self, 'prior_data') else
                None
            ),
            hash(
                self.prior_data['Y'].tostring()
                if hasattr(self,'prior_data') else
                None),
            hash(
                tuple(self.prior_gp.get_param_values())
                if hasattr(self, 'prior_gp') else
                tuple(self.get_param_values()))
        ))
    )
    def marginalize_mean(self, x,
                         dmu_dx_needed=False,
                         dmu_dtheta_needed=False):
        """

        :param x:
        :type x:
        :param dmu_dx_needed:
        :type dmu_dx_needed:
        :param dmu_dtheta_needed:
        :type dmu_dtheta_needed:
        :return:
        :rtype:
        """
        mean = self.mean(x)

        result = (mean, )

        if dmu_dx_needed:
            dmu_dx = self.dmu_dx(x)
            result += (dmu_dx, )

        if dmu_dtheta_needed:
            dmu_dtheta = self.dmu_dtheta(x)
            result += (dmu_dtheta, )

        if len(result) == 1:
            result = result[0]

        return result

    def mean(self, x):
        """

        :param x:
        :return:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def dmu_dx(self, x):
        """

        :param x:
        :type x:
        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def dmu_dtheta(self, x):
        """

        :param x:
        :type x:
        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")
