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
import scipy.optimize as spo

from .optimization_method import OptimizationMethod


class SequentialOptimization(OptimizationMethod):
    """

    """
    def __init__(self, seed):
        """

        """
        super(SequentialOptimization, self).__init__(seed)

        self.log['step_log'] = []
        self.data = None
        self.bounds = None

    def minimize(self, fun, x0, args=(),
                 bounds=(), tol=1e-06, maxiter=200, disp=True,
                 **unknown_options):
        """

        :param fun:
        :type fun:
        :param x0:
        :type x0:
        :param args:
        :type args:
        :param bounds:
        :type bounds:
        :param tol:
        :type tol:
        :param maxiter:
        :type maxiter:
        :param disp:
        :type disp:
        :param unknown_options:
        :type unknown_options:
        :return:
        :rtype:
        """
        np.random.seed(self.seed)

        self.bounds = bounds
        self.data = {
            'X': np.empty((0, len(self.bounds))),
            'Y': np.empty((0, 1))
        }

        solver_log = {}
        x_t = x0

        improvement = 0.0
        funcalls = 0
        iterations = 0

        while funcalls < maxiter and not 0.0 < improvement < tol:
            # Sample objetive function
            x_t = x_t[:(maxiter-funcalls), :]
            y_t = fun(x_t)

            # Augment the data
            self.data['X'] = np.vstack((self.data['X'], x_t))
            self.data['Y'] = np.vstack((self.data['Y'], y_t))

            # Log best and current
            improvement = 0.0
            if len(y_t) != len(self.data['Y']):
                improvement = np.min(self.data['Y'][:-len(y_t), :]) - \
                              np.min(y_t)
            funcalls += x_t.shape[0]
            iterations += 1

            # Log best and current
            step_log = {
                'funcalls': funcalls,
                'iterations': iterations,
                'improvement': improvement,
                'x_t': x_t,
                'y_t': y_t,
                'x_best': self.data['X'][np.argmin(self.data['Y']), :],
                'f_best': np.min(self.data['Y']),
                'solver_log': solver_log
            }

            self.log['step_log'].append(step_log)
            if disp:
                print(step_log)

            # Choose next point(s) to evaluate
            x_t, solver_log = self.next_sample(x_t, y_t)

        return spo.OptimizeResult(
            fun=self.log['step_log'][-1]['f_best'],
            x=self.log['step_log'][-1]['x_best'],
            nit=iterations,
            nfev=funcalls,
            success=(iterations > 1)
        )

    def next_sample(self, x_t, y_t):
        """

        :param x_t:
        :type x_t:
        :param y_t:
        :type y_t:
        :return:
        :rtype:
        """
        raise NotImplementedError("Not Implemented. This is an interface.")
