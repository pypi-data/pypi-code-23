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

import os
import unittest

from ..graft import graftPaths


class TestGraftPaths( unittest.TestCase ) :
    def testFromRoot( self ) :
        directory = 'one'
        inputNames = {
            os.path.join( 'file1' ),
            os.path.join( 'one', 'file2' ),
            os.path.join( 'one', 'subdir', 'file4' ),
            os.path.join( 'two', 'file3' ),
        }

        expectedValue = {
            os.path.join( 'one', 'file2' ),
            os.path.join( 'one', 'subdir', 'file4' ),
        }

        actualValue = graftPaths( inputNames, directory )

        self.assertEqual( expectedValue, actualValue )


    def testSubdir( self ) :
        directory = os.path.join( 'one', 'subdir' )
        inputNames = {
            os.path.join( 'file1' ),
            os.path.join( 'one', 'file2' ),
            os.path.join( 'one', 'subdir', 'file4' ),
            os.path.join( 'two', 'file3' ),
        }

        expectedValue = {
            os.path.join( 'one', 'subdir', 'file4' ),
        }

        actualValue = graftPaths( inputNames, directory )

        self.assertEqual( expectedValue, actualValue )


if __name__ == '__main__' :
    unittest.main()
