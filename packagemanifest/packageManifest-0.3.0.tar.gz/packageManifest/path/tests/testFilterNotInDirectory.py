#
# Copyright 2018 Russell Smiley
#
# This file is part of package-manifest.
#
# package-manifest is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# package-manifest is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with package-manifest.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import unittest

from ..path import filterNotInDirectory


class TestFileNotInDirectory( unittest.TestCase ) :
    def test_something( self ) :
        directory = 'one'
        inputPaths = {
            os.path.join( 'one', 'two' ),
            os.path.join( 'one', 'sub', 'file' ),
            os.path.join( 'two', 'three' ),
        }

        expectedValue = {
            os.path.join( 'one', 'two' ),
            os.path.join( 'one', 'sub', 'file' ),
        }

        actualValue = set( filterNotInDirectory( inputPaths, directory ) )

        self.assertEqual( expectedValue, actualValue )


if __name__ == '__main__' :
    unittest.main()
