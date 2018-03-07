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


class AcquisitionFunction(object):
    """

    """
    def __init__(self):
        """

        """
        self.opt_method = None

    def set_opt_method(self, opt_method):
        """

        :param opt_method:
        :type opt_method:
        :return:
        :rtype:
        """
        self.opt_method = opt_method

    def evaluate(self, point, dk_dx_needed=False):
        """

        :param point:
        :type point:
        :param dk_dx_needed:
        :type dk_dx_needed:
        :return:
        :rtype:
        """
        point = np.array(point)

        if point.ndim != 1 and point.ndim != 2:
            raise Exception("Too many dimensions")

        points = point
        if point.ndim == 1:
            points = point[None, :]

        result = self.batch_evaluate(points, dk_dx_needed)

        if point.ndim == 1:
            result = result[0, 0]

        return result

    def batch_evaluate(self, points, dk_dx_needed=False):
        """

        :param points:
        :type points:
        :param dk_dx_needed:
        :type dk_dx_needed:
        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")
