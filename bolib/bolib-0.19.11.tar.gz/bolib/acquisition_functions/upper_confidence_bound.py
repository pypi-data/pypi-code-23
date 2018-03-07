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


class UpperConfidenceBound(AcquisitionFunction):
    """

    """
    def __init__(self):
        """

        """
        self.delta = 0.1

        super(UpperConfidenceBound, self).__init__()

    def batch_evaluate(self, points, dk_dx_needed=False):
        """
        Upper Confidence Bound Acquisition Function Implementation

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

        t = self.opt_method.data['X'].shape[0]
        # TODO is this the cardinality of X?
        card_x = 20000 - t
        beta = 2 * np.log((card_x * np.power(t, 2) * np.power(np.pi, 2)) /
                          (6 * self.delta))

        result = np.array(mean) - np.sqrt(beta)*np.array(sdev)

        if not dk_dx_needed:
            return result

        # TODO grad needed
        raise Exception('gradient not implemented yet')

        # grad_mean, grad_var = model['module'].get_grad_mean_var(
        #     data, test_points,
        #     model['kernel']['module'],
        #     hyperparams, posterior_gp)
        #
        # grad_xp = - grad_mean + np.sqrt(beta)*grad_var
        #
        # return (result, -grad_xp)