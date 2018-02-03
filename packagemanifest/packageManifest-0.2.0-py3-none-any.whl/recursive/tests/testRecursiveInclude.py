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

from ..include import Include


class TestRecursiveInclude( unittest.TestCase ) :
    def testGlobalInclude( self ) :
        directory = '.'
        inputNames = {
            os.path.join( 'one' ),
            os.path.join( 'subdir', 'two' ),
            os.path.join( 'sub', 'subdir', 'three' ),
            os.path.join( 'subdir', 'four' ),
            os.path.join( 'twice' ),
        }
        inclusion = 't*'
        expectedValue = {
            os.path.join( 'subdir', 'two' ),
            os.path.join( 'twice' ),
            os.path.join( 'sub', 'subdir', 'three' ),
        }

        includeUnderTest = Include( directory, inclusion )

        actualValue = includeUnderTest.apply( inputNames, set() )

        self.assertEqual( { os.path.normpath( x ) for x in expectedValue }, actualValue )


if __name__ == '__main__' :
    unittest.main()
