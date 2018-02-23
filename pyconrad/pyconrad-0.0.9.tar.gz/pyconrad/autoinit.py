"""
Automatically initializes pyconrad if necessary
"""

__author__ = "Stephan Seitz <stephan.seitz@fau.de>"
__copyright__ = "Andreas Maier <andreas.maier@fau.de> et al."
__license__ = """
pyCONRAD, python framework for cone beam radiology
Copyright (C) 2017 Stephan Seitz <stephan.seitz@fau.de>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


import pyconrad
import pyconrad._pyconrad

if not pyconrad._pyconrad.PyConrad().is_initialized:
    pyconrad.setup_pyconrad()
    # pyconrad.setup_pyconrad(dev_dirs=['/home/stephan/projects/CONRAD'])
