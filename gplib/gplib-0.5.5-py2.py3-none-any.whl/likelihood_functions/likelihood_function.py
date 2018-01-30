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

from ..cache import CachedMethod
from ..parameters import WithParameters


class LikelihoodFunction(WithParameters):
    """

    """
    def __init__(self, hyperparams):

        self.cache = {
            'hash': 0,
            'result': None
        }

        self.gp = None

        super(LikelihoodFunction, self).__init__(hyperparams)

    def __copy__(self):

        copyed_object = self.__class__()

        copyed_object.set_hyperparams(self.get_hyperparams())

        return copyed_object

    def set_gp(self, gp):
        """

        :param gp:
        :type gp:
        :return:
        :rtype:
        """
        self.gp = gp

    @CachedMethod(lambda self, data, gradient_needed=False:
        hash((
            hash(data['X'].tostring()),
            hash(data['Y'].tostring()),
            hash(gradient_needed),
            hash(tuple(self.gp.get_param_values()))
        ))
    )
    def get_log_likelihood(self, data, gradient_needed=False):
        """

        :param data:
        :param gradient_needed:
        :return:
        """
        marginal = self.gp.inference_method.marginalize_gp(data)

        log_likelihood = self.log_likelihood(data, marginal)

        result = (log_likelihood, )

        if gradient_needed:
            dlog_likelihood_dtheta = self.dlog_likelihood_dtheta(data, marginal)
            result += (dlog_likelihood_dtheta, )

        if len(result) == 1:
            result = result[0]

        return result

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

        raise NotImplementedError("Not Implemented. This is an interface.")

    def dlog_likelihood_dtheta(self, marginal, data):
        """
        Measure the gradient log Likelihood

        :param marginal:
        :type marginal:
        :param data:
        :type data:
        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def get_predictive_mean(self, f_mean):
        """

        :param f_mean:
        :type f_mean:
        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def get_predictive_variance(self, f_variance):
        """

        :param f_variance:
        :type f_variance:
        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")
