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

class ObjectiveFunction(object):
    """

    """
    def __init__(self, d, gaussian_noise, f_bias, max_eval,
                 lower, upper, objective, objective_val, params, types):
        """

        """
        self.d = d
        self.gaussian_noise = gaussian_noise
        self.f_bias = f_bias
        self.max_eval = max_eval
        self.lower = lower
        self.upper = upper
        self.objective = objective
        self.objective_val = objective_val
        self.params = params
        self.type = types

    def evaluate(self, point, add_noise=True):
        """

        :return:
        :rtype:
        """
        point = np.array(point)

        if point.ndim != 1 and point.ndim != 2:
            raise Exception("Too many dimensions")

        points = point
        if point.ndim == 1:
            points = point[None, :]

        result = self.batch_evaluate(points)

        if point.ndim == 1:
            result = result[0, 0]

        if add_noise:
            result += np.random.randn(*result.shape) * self.gaussian_noise

        return result

    def batch_evaluate(self, points):
        """

        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def get_objective(self):
        """

        :return:
        :rtype:
        """

        return self.objective

    def get_objective_val(self):
        """

        :return:
        :rtype:
        """

        return self.objective_val

    def get_max_eval(self):
        """

        :return:
        :rtype:
        """

        return self.max_eval

    def get_bounds(self):
        """

        :return:
        :rtype:
        """

        return [
            (self.lower[i], self.upper[i])
            for i in range(self.d)
        ]
