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

from ..localName import Include as LocalInclude
from ..globalName import Exclude as GlobalExclude
from ..globalName import Include as GlobalInclude

from ..manifest import Manifest


class MockPathSet :
    def __init__( self ) :
        self.pathNames = set()
        self.rootDirectory = '.'


class TestManifest( unittest.TestCase ) :
    def setUp( self ) :
        self.pathSet = MockPathSet()

        self.pathSet.pathNames = {
            os.path.join( 'LICENSE' ),
            os.path.join( 'README' ),
            os.path.join( 'include', 'main.h' ),
            os.path.join( 'include', 'other.h' ),
        }


    def testInitialNames( self ) :
        self.testManifest = Manifest( pathSet = self.pathSet )
        self.testManifest.operations.append( LocalInclude( 'LICENSE' ) )

        actualNames = self.testManifest.apply()

        self.assertIn( 'LICENSE', actualNames )

        self.assertNotIn( os.path.join( 'README' ), actualNames )
        self.assertNotIn( os.path.join( 'include', 'main.h' ), actualNames )
        self.assertNotIn( os.path.join( 'include', 'other.h' ), actualNames )


    def testMultipleOperations( self ) :
        self.testManifest = Manifest( pathSet = self.pathSet )
        self.testManifest.operations.append( GlobalInclude( '*.h' ) )
        self.testManifest.operations.append( GlobalExclude( os.path.join( 'include', 'other.h' ) ) )

        actualNames = self.testManifest.apply()

        self.assertNotIn( os.path.join( 'LICENSE' ), actualNames )
        self.assertNotIn( os.path.join( 'README' ), actualNames )

        self.assertIn( os.path.join( 'include', 'main.h' ), actualNames )


if __name__ == '__main__' :
    unittest.main()
