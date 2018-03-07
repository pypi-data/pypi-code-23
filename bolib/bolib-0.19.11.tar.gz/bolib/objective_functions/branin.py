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


class Branin(ObjectiveFunction):
    """

    """
    def __init__(self):
        """

        """
        super(Branin, self).__init__(
            d=2,
            gaussian_noise=0,
            f_bias=0.0,
            max_eval=200,
            lower=[-5, 0],
            upper=[10, 15],
            objective=[9.42478, 2.475],
            objective_val=0.397887,
            params=['x', 'y'],
            types=[float, float]
        )

    def batch_evaluate(self, points):
        """
        Branin test function

        The number of variables n = 2.
        constraints:
        -5 <= x <= 10, 0 <= y <= 15
        three global optima:  (-pi, 12.275), (pi, 2.275), (9.42478, 2.475),
        where branin = 0.397887

        :param points:
        :type points:
        :return:
        :rtype:
        """
        x = points[:, 0][:, None]
        y = points[:, 1][:, None]
        result = np.power((y-(5.1/(4 * np.power(np.pi, 2))) *
                           np.power(x, 2)+5 * x/np.pi-6), 2)
        result += 10*(1-1/(8*np.pi))*np.cos(x)+10
        return result + self.f_bias
