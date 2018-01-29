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
import scipy.stats as sps

from .acquisition_function import AcquisitionFunction


class ProbabilityOfImprovement(AcquisitionFunction):
    """

    """
    def __init__(self):
        """

        """
        self.xi = 0.00

        super(ProbabilityOfImprovement, self).__init__()

    def batch_evaluate(self, points, dk_dx_needed=False):
        """
        Probability of Improvement Acquisition Function Implementation

        :param points:
        :type points:
        :param dk_dx_needed:
        :type dk_dx_needed:
        :return:
        :rtype:
        """
        y_mean = self.opt_method.model.mean_function.marginalize_mean(
            self.opt_method.data['X'])

        mean = self.opt_method.model.mean_function.marginalize_mean(
            points)

        var = self.opt_method.model.covariance_function.marginalize_covariance(
            points, only_diagonal=True)

        sdev = np.sqrt(var)

        F = np.min(y_mean) - mean - self.xi
        sdev[sdev == 0.0] = np.inf
        Z = F / sdev
        result = sps.norm.cdf(Z)

        if not dk_dx_needed:
            return -result

        # TODO grad needed
        raise Exception('gradient not implemented yet')
