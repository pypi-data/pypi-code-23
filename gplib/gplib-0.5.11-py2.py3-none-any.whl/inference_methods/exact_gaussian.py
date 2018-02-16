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
import scipy.linalg as spla

from .inference_method import InferenceMethod


class ExactGaussian(InferenceMethod):
    """

    """

    def marginalize(self, data):
        """ Get mean and covariance of following points """

        # Data assertions
        assert len(data['X']) == len(data['Y']), "Data is not consistent"
        assert not np.isnan(data['X']).any(), "NaN values in data['X']"
        assert not np.isinf(data['X']).any(), "Inf values in data['X']"
        assert not np.isnan(data['Y']).any(), "NaN values in data['Y']"
        assert not np.isinf(data['Y']).any(), "Inf values in data['Y']"

        mean = self.gp.mean_function.marginalize_mean(data['X'])
        covariance = self.gp.covariance_function.marginalize_covariance(
            data['X'])
        covariance /= self.gp.likelihood_function.get_param_value('noise')
        if self.gp.likelihood_function.get_optimizable_param_n():
            covariance += np.eye(covariance.shape[0])
        l_matrix = self.gp.safe_chol(covariance)
        alpha = spla.cho_solve((l_matrix, True), data['Y'] - mean)
        alpha /= self.gp.likelihood_function.get_param_value('noise')
        noise_precision = np.ones(data['X'].shape[0])[:, None]
        noise_precision /= np.sqrt(
            self.gp.likelihood_function.get_param_value('noise')
        )

        marginal = {
            'mean': mean,
            'l_matrix': l_matrix,
            'noise_precision': noise_precision,
            'alpha': alpha
        }

        return marginal
