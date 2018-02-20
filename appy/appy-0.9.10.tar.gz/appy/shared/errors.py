# Copyright (C) 2007-2018 Gaetan Delannay

# This file is part of Appy.

# Appy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Appy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Appy. If not, see <http://www.gnu.org/licenses/>.

# ------------------------------------------------------------------------------
class AppyError(Exception):
    '''Root Appy exception class'''

class ValidationError(AppyError):
    '''Represents an error that occurs on data sent to the Appy server'''

class InternalError(AppyError):
    '''Represents a programming error: something that should never occur'''

class CommercialError(AppyError):
    '''Raised when some functionality is called from the commercial version but
       is available only in the free, open source version.'''
    MSG = 'This feature is not available in the commercial version. It is ' \
          'only available in the free, open source (GPL) version of Appy.'
    def __init__(self): AppyError.__init__(self, self.MSG)
# ------------------------------------------------------------------------------
