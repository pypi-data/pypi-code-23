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


def random_sample(bounds, batch_size=1):
    """

    :param bounds:
    :type bounds:
    :param batch_size:
    :type batch_size:
    :return:
    :rtype:
    """
    x_t = np.vstack([
        np.random.uniform(
            low=lower,
            high=upper,
            size=batch_size
        )
        for lower, upper in bounds
    ]).T

    return x_t
