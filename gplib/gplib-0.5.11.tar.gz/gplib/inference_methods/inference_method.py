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


class InferenceMethod():
    """

    """
    def __init__(self):

        self.cache = {
            'hash': 0,
            'result': None
        }

        self.gp = None

    def __copy__(self):

        copyed_object = self.__class__()

        return copyed_object

    def set_gp(self, gp):
        """

        :param gp:
        :type gp:
        :return:
        :rtype:
        """
        self.gp = gp

    @CachedMethod(lambda self, data:
        hash((
            hash(data['X'].tostring()),
            hash(data['Y'].tostring()),
            hash(tuple(self.gp.get_param_values()))
        ))
    )
    def marginalize_gp(self, data):
        """

        :param data:
        :type data:
        :return:
        :rtype:
        """

        return self.marginalize(data)

    def marginalize(self, data):
        """

        :param data:
        :type data:
        :return:
        :rtype:
        """

        raise NotImplementedError("Not Implemented. This is an interface.")
