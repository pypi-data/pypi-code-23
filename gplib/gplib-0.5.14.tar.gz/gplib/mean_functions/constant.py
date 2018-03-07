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

from .mean_function import MeanFunction

from ..parameters import FixedParameter
from ..transformations import LogTransformation


class Constant(MeanFunction):
    """

    """
    def __init__(self, data):
        hyperparams = [
            FixedParameter(
                "mean", LogTransformation,
                default_value=np.mean(data['Y'])
            )
        ]

        super(Constant, self).__init__(hyperparams)

    def mean(self, x):
        """

        :param x:
        :return:
        """

        return np.ones((x.shape[0], 1)) * self.get_param_value('mean')

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
