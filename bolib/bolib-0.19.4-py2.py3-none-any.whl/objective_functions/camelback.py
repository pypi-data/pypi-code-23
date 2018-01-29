# -*- coding: utf-8 -*-
#
#    Copyright 2018 Ibai Roman
#
#    This file is part of BOlib.
#
#    BOlib is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    BOlib is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with BOlib. If not, see <http://www.gnu.org/licenses/>.

import numpy as np
from .objective_function import ObjectiveFunction


class Camelback(ObjectiveFunction):
    """

    """
    def __init__(self):
        """

        """
        super(Camelback, self).__init__(
            d=2,
            gaussian_noise=0,
            f_bias=0.0,
            max_eval=100,
            lower=[-2, -1],
            upper=[2, 1],
            objective=[0.0898, -0.7126],
            objective_val=-1.0316,
            params=['x', 'y'],
            types=[float, float]
        )

    def batch_evaluate(self, points):
        """
        Camelback test function

        The number of variables n = 2.
        constraints:
        -2 <= x <= 2, -1 <= y <= 1
        two global minima at (0.0898, -0.7126) and (-0.0898, 0.7126) where
        f(x) = -1.0316

        :param points:
        :type points:
        :return:
        :rtype:
        """
        x = points[:, 0][:, None]
        y = points[:, 1][:, None]
        x2 = np.power(x, 2)
        x4 = np.power(x, 4)
        y2 = np.power(y, 2)
        result = (np.multiply((4 - 2.1*x2 + x4/3), x2) +
                  np.multiply(x, y) +
                  np.multiply((-4+4*y2), y2))
        return result + self.f_bias
