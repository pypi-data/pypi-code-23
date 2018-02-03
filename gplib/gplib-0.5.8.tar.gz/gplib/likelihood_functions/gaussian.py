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

from .likelihood_function import LikelihoodFunction
from ..parameters import OptimizableParameter, FixedParameter
from ..transformations import LogTransformation


class Gaussian(LikelihoodFunction):
    """

    """
    def __init__(self, is_noisy=True):
        if is_noisy:
            hyperparams = [
                OptimizableParameter(
                    'noise', LogTransformation,
                    default_value=1e-08,
                    min_value=np.exp(-20), max_value=np.exp(5)
                )
            ]
        else:
            hyperparams = [
                FixedParameter(
                    "noise", LogTransformation,
                    default_value=1.0
                )
            ]

        super(Gaussian, self).__init__(hyperparams)

    def log_likelihood(self, data, marginal):
        """
        Measure the log Likelihood

        :param data:
        :type data:
        :param marginal:
        :type marginal:
        :return:
        :rtype:
        """
        llikelihood = -np.sum(np.log(np.diag(marginal['l_matrix']))) - \
            0.5 * np.dot(
                    (data['Y'] - marginal['mean']).T,
                    marginal['alpha']
                )[0, 0] - \
            0.5 * marginal['l_matrix'].shape[0] * \
                np.log(2.0 * np.pi * self.get_param_value('noise'))

        return llikelihood

    def dlog_likelihood_dtheta(self, data, marginal):
        """
        Measure the gradient log Likelihood

        :param data:
        :type data:
        :param marginal:
        :type marginal:
        :return:
        :rtype:
        """
        k_inv = spla.cho_solve(
            (marginal['l_matrix'], True),
            np.eye(marginal['l_matrix'].shape[0]))
        k_inv /= self.get_param_value('noise')
        jacobian = np.outer(marginal['alpha'],
                            marginal['alpha']) - k_inv

        grad_llikelihood = []

        # TODO
        if self.gp.mean_function.get_optimizable_param_n():
            pass

        if self.gp.covariance_function.get_optimizable_param_n():
            # Log amplitude gradient.
            _, dk_dtheta = self.gp.covariance_function.marginalize_covariance(
                data['X'], dk_dtheta_needed=True)
            if self.gp.covariance_function.get_hyperparam('alpha'):
                dk_dov2, dk_dalpha, dk_dl = dk_dtheta
            else:
                dk_dov2, dk_dl = dk_dtheta
            output_variance2 = self.gp.covariance_function.get_hyperparam(
                'output_variance2')
            dk_dov2 = output_variance2.grad_trans(dk_dov2)
            grad_llikelihood.append(
                self._dlog_likelihood_dtheta(dk_dov2, jacobian))

            if self.gp.covariance_function.get_hyperparam('alpha'):
                alpha = self.gp.covariance_function.get_hyperparam('alpha')
                dk_dalpha = alpha.grad_trans(dk_dalpha)
                grad_llikelihood.append(
                    self._dlog_likelihood_dtheta(dk_dalpha, jacobian))

            # Log length scale gradients.
            lengthscale = \
                self.gp.covariance_function.get_hyperparam('lengthscale')
            ard = data['X'].shape[1] == \
                lengthscale.get_optimizable_param_n()
            dk_dl = lengthscale.grad_trans(dk_dl)
            for i in range(data['X'].shape[1]):
                dk_dl_i = dk_dl[:, :, i]
                if not ard and i != 0:
                    grad_llikelihood[-1] += \
                        self._dlog_likelihood_dtheta(dk_dl_i, jacobian)
                else:
                    grad_llikelihood.append(
                        self._dlog_likelihood_dtheta(dk_dl_i, jacobian))

        # Log noise gradient.
        if self.get_optimizable_param_n():
            dk_dn = np.eye(data['X'].shape[0])
            noise = self.get_hyperparam('noise')
            dk_dn = noise.grad_trans(dk_dn)
            grad_llikelihood.append(
                self._dlog_likelihood_dtheta(dk_dn, jacobian))

        return grad_llikelihood

    @staticmethod
    def _dlog_likelihood_dtheta(dk_dtheta, jacobian):
        """
        Measure the gradient of the log Likelihood

        :param jacobian:
        :return:
        """
        return 0.5 * np.trace(np.dot(jacobian, dk_dtheta))

    def get_predictive_mean(self, f_mean):
        """

        :param f_mean:
        :type f_mean:
        :return:
        :rtype:
        """
        y_mean = f_mean

        return y_mean

    def get_predictive_variance(self, f_variance):
        """

        :param f_variance:
        :type f_variance:
        :return:
        :rtype:
        """
        y_variance = f_variance
        if self.get_optimizable_param_n():
            y_variance += (
                    np.eye(y_variance.shape[1]) * self.get_param_value('noise')
            )

        return y_variance
