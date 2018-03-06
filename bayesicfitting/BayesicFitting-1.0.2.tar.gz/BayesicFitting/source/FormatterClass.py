from __future__ import print_function

import numpy as numpy
from numpy import ndarray
from numpy import float64
from numpy import int64
import math

__author__ = "Do Kester"
__year__ = 2017
__license__ = "GPL3"
__version__ = "0.9"
__maintainer__ = "Do"
__status__ = "Development"

#  * This file is part of the BayesicFitting package.
#  *
#  * BayesicFitting is free software: you can redistribute it and/or modify
#  * it under the terms of the GNU Lesser General Public License as
#  * published by the Free Software Foundation, either version 3 of
#  * the License, or ( at your option ) any later version.
#  *
#  * BayesicFitting is distributed in the hope that it will be useful,
#  * but WITHOUT ANY WARRANTY; without even the implied warranty of
#  * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  * GNU Lesser General Public License for more details.
#  *
#  * The GPL3 license can be found at <http://www.gnu.org/licenses/>.
#  *
#  *    2017        Do Kester


class Formatter( object ) :
    """
    Format numbers or arrays of numbers in a nice format.

    Attributes
    ----------
    gllen : int
        global line length
    gindent : int
        number of indentation spaces
    gmax : int
        number of items to display
    fmt : dict of {type: str}
        type : "float64" | "int64"
        str  : format string
    """

    def __init__( self, format=None, indent=0, linelength=80, max=5 ):
        """
        Initialize the formatter with new default values.

        Parameters
        ----------
        format : dict {namestring : formatstring }
            name : "float64" or "int64"
            fmt  : " %fmt"
        indent : int
            number of spaces to indent *after* the first line
            Default is 0
        linelength : int
            length of the lines produced
            Default is 80
        max : int or None
            maximum number of items displayed followed by ... if there are more
            None displays all
            Default is 5
        """

#       global gllen, gindent, gmax

        if format is not None :
            self.fmt = { "float64" : " %8.3f", "int64" : " %8d" }
        else :
            for k in format.keys() :
                self.fmt[k] = format[k]

        self.indent = indent
        self.linelen = linelength
        self.max = max


    def formatter( array, format=None, indent=None, linelength=None, max=-1 ) :
        """
        Format a number or an array nicely into a string

        Parameters override defaults given earlier with init().

        Parameters
        ----------
        array : array_like or number
            number or list of numbers or n-dim array of numbers
        format : None or string
            format applying to one item of array
            Default is "8.3f" for float and "8d" for int
        indent : None or int
            number of spaces to indent *after* the first line
            Default is 0
        linelength : None or int
            length of the lines produced
            Default is 80
        max : None or int
            maximum number of items displayed followed by ... if there are more
            None displays all
            Default is 5

        Returns
        -------
        string : containing the formatted array

        """
        if indent is None :
            indent = self.indent
        if linelength is None :
            linelength = self.linelen
        if max is not None and max >= 0 :
            max = self.max
        count = indent
        dent = indent
        llen = linelength
        mx = max
        nwl = False
        sp = 0

        if not isinstance( array, ndarray ) :
            array = numpy.asarray( array )

        if format is None :
            format = self.format[str(array.dtype)]

        fmtlen = len( format % 1 )
        nwl = False

        result = ""
        result = self.recurse( result, array, format, fmtlen, indent, nwl, max )
        return result

    def recurse( self, result, array, format, fmtlen, indent, nwl, max ) :

        if array.size == 1 :
            if count + fmtlen > llen :
                result += ( "\n%s" % self.spaces( sp + indent ) )
                count = indent
            result += ( format % array )
            count += fmtlen
            return result

        shp = array.shape
        if sp > 0 and nwl :
            result += ( "\n%s" % self.spaces( sp + indent ) )
        result += ( "[" )
        nwl = False
        sp += 1
        shp0 = shp[0] if max is None else min( shp[0], max )
        for k in range( shp0 ) :
            result = self.recurse( result, array[k], format, fmtlen, indent, nwl, max )
            nwl = True
        if max is not None and shp[0] > max :
            result += " ..."
        result += ( "]"  )
        count = 0
        sp -=1
        return result

    def spaces( self, int ) :
        return ( " " * int )

