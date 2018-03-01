## Function library file for my math functions
#
# @file		    math_functions.py
# @author	    Tobias Ecklebe tobias.ecklebe@outlook.de
# @date		    05.11.2017
# @version	    0.1.0
# @note		    This file includes functions as libary that i think are great for different projects.\n\n
#               To use this file:  from pylibcklb.math-library.math_functions import SomeClassOrFunction\n  
#
# @pre          The library was developed with python 3.6 64 bit
#
# @bug          No bugs at the moment.
#
# @warning      No warnings at the moment
#
# @copyright    pylibcklb package
#               Copyright (C) 2017  Tobias Ecklebe
#
#               This program is free software: you can redistribute it and/or modify
#               it under the terms of the GNU Lesser General Public License as published by
#               the Free Software Foundation, either version 3 of the License, or
#               (at your option) any later version.
#
#               This program is distributed in the hope that it will be useful,
#               but WITHOUT ANY WARRANTY; without even the implied warranty of
#               MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#               GNU Lesser General Public License for more details.
#
#               You should have received a copy of the GNU Lesser General Public License
#               along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import numpy as np
from pylibcklb.metadata import PackageVariables
Debug = cDebug(PackageVariables.DebugLevel)

## Documentation for a method to get an normal random number
# @note https://docs.scipy.org/doc/numpy-1.13.0/reference/generated/numpy.random.normal.html
# @param loc  Mean (“centre”) of the distribution.
# @param scale Standard deviation (spread or “width”) of the distribution.
# @param size   Output shape. If the given shape is, e.g., (m, n, k), then m * n * k samples are drawn. If size is None (default), a single value is returned if loc and 
#               scale are both scalars. Otherwise, np.broadcast(loc, scale).size samples are drawn.
# @return Drawn samples from the parameterized normal distribution.
def GetNormalRandomNumber(loc=0.0, scale=1.0, size=None):
    return np.random.normal(loc, scale, size)

