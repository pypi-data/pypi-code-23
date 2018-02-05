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

from ..manifest import loadYamlData


class TestLoadYaml( unittest.TestCase ) :
    def setUp( self ) :
        thisDir = os.path.dirname( __file__ )

        self.dataDir = os.path.join( thisDir, 'data' )


    def test_something( self ) :
        yamlFilePath = os.path.join( self.dataDir, 'sampleManifest.yml' )

        yamlData = loadYamlData( yamlFilePath )

        self.assertTrue( isinstance( yamlData, list ) )
        self.assertEqual( 8, len( yamlData ) )


if __name__ == '__main__' :
    unittest.main()
