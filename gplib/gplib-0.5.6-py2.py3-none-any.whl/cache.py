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

import copy


class CachedMethod(object):
    """

    """
    def __init__(self, hash_function):

        self.hash_function = hash_function

    def __call__(self, method):
        """

        :param method:
        :type method:
        :return:
        :rtype:
        """

        def method_wrapper(this, *args, **kwargs):
            """

            :param this:
            :type this:
            :param args:
            :type args:
            :param kwargs:
            :type kwargs:
            :return:
            :rtype:
            """

            hash_value = self.hash_function(this, *args, **kwargs)

            if hash_value == this.cache['hash']:
                return copy.deepcopy(this.cache['result'])

            result = method(this, *args, **kwargs)
            this.cache['hash'] = hash_value
            this.cache['result'] = copy.deepcopy(result)

            return result

        return method_wrapper
