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


class Hartmann(ObjectiveFunction):
    """

    """
    def __init__(self):
        """

        """
        super(Hartmann, self).__init__(
            d=6,
            gaussian_noise=0,
            f_bias=0.0,
            max_eval=200,
            lower=[0, 0, 0, 0, 0, 0],
            upper=[1, 1, 1, 1, 1, 1],
            objective=[0.20169, 0.150011, 0.476874,
                       0.275332, 0.311652, 0.6573],
            objective_val=-3.32236,
            params=['x', 'y', 'z', 'a', 'b', 'c'],
            types=[float, float, float, float, float, float]
        )

    def batch_evaluate(self, points):
        """
        6d Hartmann test function

        constraints:
        0 <= xi <= 1, i = 1..6
        global optimum at (0.20169, 0.150011, 0.476874,
                           0.275332, 0.311652, 0.6573)
        where har6 = -3.32236

        :param points:
        :type points:
        :return:
        :rtype:
        """
        x = points[:, 0][:, None]
        y = points[:, 1][:, None]
        z = points[:, 2][:, None]
        a = points[:, 3][:, None]
        b = points[:, 4][:, None]
        c = points[:, 5][:, None]
        value = np.array([x, y, z, a, b, c])

        a = np.array([[10.0, 3.0, 17.0, 3.5, 1.7, 8.0],
                      [0.05, 10.0, 17.0, 0.1, 8.0, 14.0],
                      [3.0, 3.5, 1.7, 10.0, 17.0, 8.0],
                      [17.0, 8.0, 0.05, 10.0, 0.1, 14.0]])
        c = np.array([1.0, 1.2, 3.0, 3.2])
        p = np.array([[0.1312, 0.1696, 0.5569, 0.0124, 0.8283, 0.5886],
                      [0.2329, 0.4135, 0.8307, 0.3736, 0.1004, 0.9991],
                      [0.2348, 0.1451, 0.3522, 0.2883, 0.3047, 0.6650],
                      [0.4047, 0.8828, 0.8732, 0.5743, 0.1091, 0.0381]])
        s = 0
        for i in [0, 1, 2, 3]:
            sm = a[i, 0]*(value[0]-p[i, 0])**2
            sm += a[i, 1]*(value[1]-p[i, 1])**2
            sm += a[i, 2]*(value[2]-p[i, 2])**2
            sm += a[i, 3]*(value[3]-p[i, 3])**2
            sm += a[i, 4]*(value[4]-p[i, 4])**2
            sm += a[i, 5]*(value[5]-p[i, 5])**2
            s += c[i]*np.exp(-sm)
        result = s
        return - result + self.f_bias
