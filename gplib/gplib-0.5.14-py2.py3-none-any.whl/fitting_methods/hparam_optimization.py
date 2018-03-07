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

import time

import numpy as np
import scipy.optimize as spo

from .fitting_method import FittingMethod


class HparamOptimization(FittingMethod):
    """

    """

    def __init__(self, ls_method="Powell", save_opt=True):

        if ls_method in ["Newton-CG", "dogleg", "trust-ncg"]:
            raise NotImplementedError("Hessian not implemented for {}".format(
                ls_method))
        self.grad_needed = ls_method in [
            "CG", "BFGS", "Newton-CG", "L-BFGS-B",
            "TNC", "SLSQP", "dogleg", "trust-ncg"
        ]
        self.bounded_search = ls_method in [
            "L-BFGS-B", "TNC", "SLSQP"
        ]
        if ls_method == "Powell":
            self.ls_method = self.mod_powell
        else:
            self.ls_method = ls_method
        self.save_opt = save_opt
        self.log = {
            'fun_calls': 0,
            'time': 0.0,
            'best_params': [],
            'best_estimator': None,
            'improvement_count': 0,
            'restart_count': 0,
            'last_improvement': {
                'restart': 0,
                'fun_call': 0,
                'ls_fun_call': 0
            }
        }
        super(HparamOptimization, self).__init__()

    def get_log(self):
        """

        :return:
        :rtype:
        """
        return self.log

    def fit(self, data, max_fun_call=5000, max_ls_fun_call=1000):
        """
        optimize hyperparams

        :param data:
        :type data:
        :param max_fun_call:
        :type max_fun_call:
        :param max_ls_fun_call:
        :type max_ls_fun_call:
        :return:
        :rtype:
        """
        # Get estimator wrappers ready
        bounds = None
        if self.bounded_search:
            bounds = self.gp.get_param_bounds(trans=True)
        estimator_opt_wrapper = self.get_estimator_wrapper(
            data,
            max_fun_call,
            max_ls_fun_call,
            grad_needed=self.grad_needed
        )

        # Main loop
        self.log['fun_calls'] = 0
        self.log['time'] = 0.0
        self.log['best_params'] = []
        self.log['best_estimator'] = np.inf
        self.log['improvement_count'] = 0
        self.log['restart_count'] = 0
        self.log['last_improvement']['restart'] = 0
        self.log['last_improvement']['fun_call'] = 0
        self.log['last_improvement']['ls_fun_call'] = 0

        self.log['current_params'] = None
        self.log['current_estimator'] = np.inf
        self.log['current_ls_fun_calls'] = 0

        start = time.time()

        while self.log['fun_calls'] < max_fun_call:
            # run optimization
            self.log['current_estimator'] = np.inf
            self.log['current_ls_fun_calls'] = 0
            x_0 = self.gp.get_param_values(trans=True)
            try:
                spo.minimize(
                    estimator_opt_wrapper,
                    x_0, method=self.ls_method,
                    jac=self.grad_needed, bounds=bounds,
                    options={
                        'disp': False
                    }
                )
            except (AssertionError, np.linalg.linalg.LinAlgError):
                pass

            self.log['restart_count'] += 1
            if self.log['current_estimator'] < self.log['best_estimator']:
                self.log['best_estimator'] = self.log['current_estimator']
                self.log['best_params'] = self.log['current_params']
                self.log['improvement_count'] += 1
                self.log['last_improvement']['restart'] = \
                    self.log['restart_count']
                self.log['last_improvement']['fun_call'] = \
                    self.log['fun_calls']
                self.log['last_improvement']['ls_fun_call'] = \
                    self.log['current_ls_fun_calls']
            self.gp.set_params_at_random(trans=True)

        end = time.time()
        self.log['time'] = end - start

        del self.log['current_estimator']
        del self.log['current_params']
        del self.log['current_ls_fun_calls']

        if not self.log['best_params']:
            raise Exception("No params were found")

        self.gp.set_param_values(self.log['best_params'], trans=False)

        if self.save_opt:
            self.gp.save_current_as_optimized()

    def get_estimator_wrapper(self, data,
                              max_fun_call, max_ls_fun_call,
                              grad_needed=False):
        """

        :param data:
        :type data:
        :param max_fun_call:
        :type max_fun_call:
        :param max_ls_fun_call:
        :type max_ls_fun_call:
        :param grad_needed:
        :type grad_needed:
        :return:
        :rtype:
        """

        def estimator_wrapper(mod_params):
            """
            estimator wrapper to optimize hyperparameters
            :param mod_params:
            :return:
            """
            self.log['fun_calls'] += 1
            self.log['current_ls_fun_calls'] += 1

            assert self.log['fun_calls'] < max_fun_call,\
                "Funcall limit reached"
            assert self.log['current_ls_fun_calls'] < max_ls_fun_call,\
                "LS Funcall limit reached"

            likelihood = np.Inf
            grad_likelihood = np.random.uniform(-1, 1, len(mod_params))

            try:
                self.gp.set_param_values(mod_params, trans=True)
                likelihood = self.gp.likelihood_function.get_log_likelihood(
                    data, gradient_needed=grad_needed
                )
                if grad_needed:
                    likelihood, grad_likelihood = likelihood
                    grad_likelihood = -np.array(grad_likelihood)
                likelihood = -float(likelihood)
            except np.linalg.linalg.LinAlgError as ex:
                raise ex
            except AssertionError:
                pass

            if likelihood < self.log['current_estimator']:
                self.log['current_estimator'] = likelihood
                self.log['current_params'] = self.gp.get_param_values()

            if grad_needed:
                return likelihood, grad_likelihood

            return likelihood

        return estimator_wrapper

    @staticmethod
    def mod_powell(fun, x0, args=(), **kwargs):
        """

        :return:
        :rtype:
        """
        rand_perm = np.random.permutation(len(x0))
        direc = np.eye(len(x0))
        direc = direc[rand_perm]

        spo.fmin_powell(fun, x0, args, disp=kwargs['disp'], direc=direc)
