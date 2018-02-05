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

from ..prune import Prune


class TestPrune( unittest.TestCase ) :
    def testFromRootEmptyPrevious( self ) :
        directory = 'one'
        inputNames = {
            os.path.join( 'file1' ),
            os.path.join( 'one', 'file2' ),
            os.path.join( 'one', 'subdir', 'file4' ),
            os.path.join( 'two', 'file3' ),
        }

        expectedValue = set()

        pruneUnderTest = Prune( directory )

        actualValue = pruneUnderTest.apply( inputNames, set() )

        self.assertEqual( expectedValue, actualValue )


    def testFromRootNonemptyPrevious( self ) :
        directory = 'one'
        inputNames = {
            os.path.join( 'file1' ),
            os.path.join( 'one', 'file2' ),
            os.path.join( 'one', 'subdir', 'file4' ),
            os.path.join( 'two', 'file3' ),
        }

        expectedValue = {
            os.path.join( 'file1' ),
        }

        pruneUnderTest = Prune( directory )

        actualValue = pruneUnderTest.apply( inputNames, {
            os.path.join( 'file1' ),
            os.path.join( 'one', 'file2' ),
        } )

        self.assertEqual( expectedValue, actualValue )


if __name__ == '__main__' :
    unittest.main()
