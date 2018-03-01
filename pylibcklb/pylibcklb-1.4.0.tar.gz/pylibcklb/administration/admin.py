## Admin file for the pylibcklb package
#
# @file		    admin.py
# @author	    Tobias Ecklebe
# @date		    02.12.2017
# @version	    0.1.0
# @note		    This file includes classes as libary that i think are great for different projects.\n\n
#               To use this file:  from pylibcklb.administration-library.admin import SomeClassOrFunction\n   
# 
# @pre          The programm was developed with python 3.6 64Bit
#
# @bug          No bugs at the moment.
#
# @warning      No warnings at the moment. 
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

import sys, os, traceback, types

## Documentation for a method that checks if the user is part of the admin group or not
# @note         The methode comes from https://github.com/dlcowen/dfirwizard/blob/master/admin.py but where original written from Preston Landers 2010 and has his COPYRIGHT!
#               https://gist.github.com/Preston-Landers/267391562bc96959eb41
#               The code where modified so that is works under python 3.6 64Bit
# @return Boolean extract from string
def isUserAdmin():

    if os.name == 'nt':
        import ctypes
        # WARNING: requires Windows XP SP2 or higher!
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            traceback.print_exc()
            print ("Admin check failed, assuming not an admin.")
            return False
    elif os.name == 'posix':
        # Check for root on Posix
        return os.getuid() == 0
    else:
        raise RuntimeError("Unsupported operating system for this module: %s" % (os.name,))

