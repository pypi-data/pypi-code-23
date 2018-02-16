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


class Parametrizable(object):
    """

    """

    def is_array(self):
        """

        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def set_params_at_random(self, trans=True):
        """

        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def set_param_values(self, params, trans=False):
        """

        :param params:
        :type params:
        :param trans:
        :type trans:
        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def save_current_as_optimized(self):
        """

        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def set_params_to_default(self):
        """

        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def get_param_values(self, trans=False):
        """

        :param trans:
        :type trans:
        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def get_current_value(self, trans=False):
        """

        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def get_param_keys(self):
        """

        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def get_name(self):
        """

        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def get_param_bounds(self, trans=False):
        """

        :param trans:
        :type trans:
        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")

    def get_optimizable_param_n(self):
        """

        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")


class WithParameters(Parametrizable):
    """

    """
    def __init__(self, hyperparameters):
        """

        :param hyperparameters:
        :type hyperparameters:
        """

        self.set_hyperparams(hyperparameters)

    def get_hyperparam(self, name):
        """

        :param name:
        :type name:
        :return:
        :rtype:
        """
        for hyperparameter in self.hyperparameters:
            hp_name = hyperparameter.get_name()
            if hp_name == name:
                return hyperparameter

    def get_hyperparams(self):
        """

        :return:
        :rtype:
        """

        return self.hyperparameters

    def set_hyperparams(self, hyperparams):
        """

        :param hyperparams:
        :type hyperparams:
        :return:
        :rtype:
        """

        assert type(hyperparams) is list,\
            "hyperparams must be a list"
        self.hyperparameters = hyperparams

    def get_param_value(self, name):
        """

        :param name:
        :type name:
        :return:
        :rtype:
        """
        hyperparam = self.get_hyperparam(name)
        return hyperparam.get_current_value()

    def is_array(self):
        """

        :return:
        :rtype:
        """

        raise True

    def set_params_at_random(self, trans=False):
        """

        :return:
        :rtype:
        """

        for hyperparameter in self.hyperparameters:
            hyperparameter.set_params_at_random(trans)

    def set_param_values(self, params, trans=False):
        """

        :param params:
        :type params:
        :param trans:
        :type trans:
        :return:
        :rtype:
        """

        assert (len(params) == self.get_optimizable_param_n()),\
            "length of params is not correct"

        i = 0
        for hyperparameter in self.hyperparameters:
            number_of_params = \
                hyperparameter.get_optimizable_param_n()
            param_slice = slice(i, i + number_of_params)
            hyperparameter.set_param_values(
                params[param_slice], trans)
            i += number_of_params

    def save_current_as_optimized(self):
        """

        :return:
        :rtype:
        """

        for hyperparameter in self.hyperparameters:
            hyperparameter.save_current_as_optimized()

    def set_params_to_default(self):
        """

        :return:
        :rtype:
        """

        for hyperparameter in self.hyperparameters:
            hyperparameter.set_params_to_default()

    def get_param_values(self, trans=False):
        """

        :param trans:
        :type trans:
        :return:
        :rtype:
        """

        params = []
        for hyperparameter in self.hyperparameters:
            params += hyperparameter.get_param_values(trans)

        return params

    def get_current_value(self, trans=False):
        """

        :return:
        :rtype:
        """

        params = []
        for hyperparameter in self.hyperparameters:
            hp_value = hyperparameter.get_current_value(trans)
            if not hasattr(hp_value, "__len__"):
                hp_value = [hp_value]
            params += hp_value

        return params

    def get_param_keys(self):
        """

        :return:
        :rtype:
        """

        params = []

        for hyperparameter in self.hyperparameters:
            name = self.get_name()
            params += [
                name + "_" + item for item in hyperparameter.get_param_keys()
            ]

        return params

    def get_name(self):
        """

        :return:
        :rtype:
        """

        return self.__class__.__name__

    def get_param_bounds(self, trans=False):
        """

        :param trans:
        :type trans:
        :return:
        :rtype:
        """

        bounds = []

        for hyperparameter in self.hyperparameters:
            bounds += hyperparameter.get_param_bounds(trans)

        return bounds

    def get_optimizable_param_n(self):
        """

        :return:
        :rtype:
        """

        n_optimizable = 0

        for hyperparameter in self.hyperparameters:
            n_optimizable += hyperparameter.get_optimizable_param_n()

        return n_optimizable


class OptimizableParameter(Parametrizable):
    """

    """
    def __init__(self, name, transformation, default_value=1.0,
                 min_value=-np.inf, max_value=np.inf,
                 jitter_sd=0.1,
                 restart_function=None):
        """

        :param name:
        :type name:
        :param transformation:
        :type transformation:
        :param default_value:
        :type default_value:
        :param min_value:
        :type min_value:
        :param max_value:
        :type max_value:
        :param jitter_sd:
        :type jitter_sd:
        :param restart_function:
        :type restart_function:
        """

        self.name = name
        self.transformation = transformation
        assert (np.all(min_value <= default_value) and
                np.all(default_value <= max_value)),\
            "{} is out of bounds".format(self.name)
        self.default_value = default_value
        self.array = hasattr(self.default_value, "__len__")
        self.current_value = self.default_value
        self.optimized_value = None

        self.dims = 1
        if self.array:
            self.dims = len(self.default_value)

        self.min_value = min_value
        self.max_value = max_value

        self.jitter_sd = jitter_sd

        self.restart_function = restart_function

    def set_min_value(self, min_value):
        """

        :param min_value:
        :type min_value:
        :return:
        :rtype:
        """
        self.min_value = min_value

    def set_max_value(self, max_value):
        """

        :param max_value:
        :type max_value:
        :return:
        :rtype:
        """
        self.max_value = max_value

    def grad_trans(self, df):
        """

        :param df:
        :type df:
        :return:
        :rtype:
        """

        return self.transformation.grad_trans(self.current_value, df)

    def is_array(self):
        """

        :return:
        :rtype:
        """
        return self.array

    def set_params_at_random(self, trans=False):
        """

        :return:
        :rtype:
        """
        min_value = self.min_value
        max_value = self.max_value
        if trans:
            min_value = self.transformation.trans(min_value)
            max_value = self.transformation.trans(max_value)

        if self.optimized_value is None:
            if self.restart_function is not None:
                current_value = None
                while not (current_value is not None and
                           np.all(min_value < current_value) and
                           np.all(current_value < max_value)):
                    current_value = self.restart_function()
            else:
                current_value = np.array(np.random.uniform(
                    min_value, max_value, self.dims
                ))
        else:
            optimized_value = self.optimized_value
            if trans:
                optimized_value = self.transformation.trans(optimized_value)
            current_value = None
            while not (current_value is not None and
                       np.all(min_value < current_value) and
                       np.all(current_value < max_value)):
                current_value = np.array(np.random.normal(
                    loc=0.0,
                    scale=self.jitter_sd,
                    size=self.dims
                ))
                current_value += optimized_value

        self.set_param_values(current_value, trans=trans)

    def set_param_values(self, params, trans=False):
        """

        :param params:
        :type params:
        :param trans:
        :type trans:
        :return:
        :rtype:
        """

        assert len(params) == self.dims, \
            "length of {} is not correct".format(self.name)

        if trans:
            if self.array:
                params = self.transformation.inv_trans(params).tolist()
            else:
                params = self.transformation.inv_trans(params)

        assert (np.all(self.min_value <= params) and
                np.all(params <= self.max_value)), \
            "{} is out of bounds".format(self.name)

        if self.array is False:
            self.current_value = params[0]
        else:
            self.current_value = params

    def save_current_as_optimized(self):
        """

        :return:
        :rtype:
        """
        self.optimized_value = self.current_value

    def set_params_to_default(self):
        """

        :return:
        :rtype:
        """
        self.current_value = self.default_value
        self.optimized_value = None

    def get_param_values(self, trans=False):
        """

        :param trans:
        :type trans:
        :return:
        :rtype:
        """
        current_value = self.get_current_value(trans=trans)

        if self.array:
            return current_value
        return [current_value]

    def get_current_value(self, trans=False):
        """

        :return:
        :rtype:
        """

        assert self.current_value is not None, \
            "{} has not been initialized".format(self.name)

        current_value = self.current_value
        if trans:
            current_value = self.transformation.trans(current_value)
            if self.array:
                current_value = current_value.tolist()

        return current_value

    def get_param_keys(self):
        """

        :return:
        :rtype:
        """

        if self.dims == 1:
            return [self.get_name()]

        return [
            "{}_d{}".format(self.get_name(), dim) for dim in range(self.dims)
        ]

    def get_name(self):
        """

        :return:
        :rtype:
        """

        return self.name

    def get_param_bounds(self, trans=False):
        """

        :param trans:
        :type trans:
        :return:
        :rtype:
        """

        min_value = self.min_value
        max_value = self.max_value

        if trans:
            min_value = self.transformation.trans(min_value)
            max_value = self.transformation.trans(max_value)

        return [(min_value, max_value)] * self.dims

    def get_optimizable_param_n(self):
        """

        :return:
        :rtype:
        """

        return self.dims


class FixedParameter(Parametrizable):
    """

    """
    def __init__(self, name, transformation, default_value):
        """

        :param name:
        :type name:
        :param transformation:
        :type transformation:
        :param default_value:
        :type default_value:
        """

        self.name = name
        self.transformation = transformation
        self.default_value = default_value
        self.array = hasattr(self.default_value, "__len__")
        self.current_value = self.default_value

    def is_array(self):
        """

        :return:
        :rtype:
        """
        return self.array

    def set_params_at_random(self, trans=False):
        """

        :return:
        :rtype:
        """
        pass

    def set_param_values(self, params, trans=False):
        """

        :param params:
        :type params:
        :param trans:
        :type trans:
        :return:
        :rtype:
        """
        pass

    def save_current_as_optimized(self):
        """

        :return:
        :rtype:
        """
        pass

    def set_params_to_default(self):
        """

        :return:
        :rtype:
        """
        pass

    def get_param_values(self, trans=False):
        """

        :param trans:
        :type trans:
        :return:
        :rtype:
        """

        return []

    def get_current_value(self, trans=False):
        """

        :return:
        :rtype:
        """

        assert self.current_value is not None, \
            "{} has not been initialized".format(self.name)

        current_value = self.current_value
        if trans:
            current_value = self.transformation.trans(current_value)
            if self.array:
                current_value = current_value.tolist()

        return current_value

    def get_param_keys(self):
        """

        :return:
        :rtype:
        """
        return []

    def get_name(self):
        """

        :return:
        :rtype:
        """

        return self.name

    def get_param_bounds(self, trans=False):
        """

        :param trans:
        :type trans:
        :return:
        :rtype:
        """
        return []

    def get_optimizable_param_n(self):
        """

        :return:
        :rtype:
        """
        return 0
