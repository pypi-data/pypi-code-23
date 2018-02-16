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


class Transformation(object):
    """

    """
    @staticmethod
    def trans(x):
        """

        :param x:
        :return:
        """
        raise NotImplementedError("Not Implemented. This is an interface.")

    @staticmethod
    def inv_trans(x):
        """

        :param x:
        :return:
        """
        raise NotImplementedError("Not Implemented. This is an interface.")

    @staticmethod
    def grad_trans(f, df):
        """

        :param f:
        :param df:
        :return:
        """
        raise NotImplementedError("Not Implemented. This is an interface.")


class LogTransformation(Transformation):
    """

    """

    @staticmethod
    def trans(x):
        """

        :param x:
        :return:
        """
        return np.log(x)

    @staticmethod
    def inv_trans(x):
        """

        :param x:
        :return:
        """
        return np.exp(x)

    @staticmethod
    def grad_trans(f, df):
        """

        :param f:
        :param df:
        :return:
        """
        return f * df


class NoneTransformation(Transformation):
    """

    """

    @staticmethod
    def trans(x):
        """

        :param x:
        :return:
        """
        if hasattr(x, "__len__"):
            return np.array(x)
        return x

    @staticmethod
    def inv_trans(x):
        """

        :param x:
        :return:
        """
        if hasattr(x, "__len__"):
            return np.array(x)
        return x

    @staticmethod
    def grad_trans(f, df):
        """

        :param f:
        :param df:
        :return:
        """
        # TODO this should be reviewed
        return f * df
