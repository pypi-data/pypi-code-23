#
# Copyright 2017 Russell Smiley
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
A packaging utility for creating packages of files for distribution based on a YAML manifest.
"""

import os.path


here = os.path.abspath( os.path.dirname( __file__ ) )

with open( os.path.join( here, 'VERSION' ) ) as versionFile :
    version = versionFile.read()

__version__ = version.strip()

from .main import main
