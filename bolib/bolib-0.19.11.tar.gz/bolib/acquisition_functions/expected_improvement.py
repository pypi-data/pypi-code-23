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


class ExpectedImprovement(AcquisitionFunction):
    """

    """
    def __init__(self):
        """

        """
        self.xi = 0.00

        super(ExpectedImprovement, self).__init__()

    def batch_evaluate(self, points, dk_dx_needed=False):
        """
        Expected Improvement Acquisition Function Implementation

        :param points:
        :type points:
        :param dk_dx_needed:
        :type dk_dx_needed:
        :return:
        :rtype:
        """
        mean = self.opt_method.model.mean_function.marginalize_mean(
            points)

        var = self.opt_method.model.covariance_function.marginalize_covariance(
            points, only_diagonal=True)

        sdev = np.sqrt(var)

        F = np.min(self.opt_method.data['Y']) - mean + self.xi
        sdev[sdev == 0.0] = np.inf
        Z = F/sdev
        cdf_z = sps.norm.cdf(Z)
        pdf_z = sps.norm.pdf(Z)
        result = np.array(F)*cdf_z+np.array(sdev)*pdf_z
        result[sdev == np.inf] = 0.0

        if not dk_dx_needed:
            return -result

        # TODO grad needed
        raise Exception('gradient not implemented yet')
        # grad_mean, grad_var = model['module'].get_grad_mean_var(
        #     data, test_points,
        #     model['kernel']['module'],
        #     hyperparams, posterior_gp)
        #
        # grad_xp = np.multiply(cdf_z, grad_mean) - np.multiply(pdf_z, grad_var)
        #
        # return (-result, grad_xp)
