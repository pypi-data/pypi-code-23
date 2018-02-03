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

import unittest

from ..globalName import Include as GlobalInclude
from ..localName import Exclude as LocalExclude
from ..tree import Prune

from ..manifest import \
    Manifest, \
    YamlNotFound


class TestManifestYaml( unittest.TestCase ) :
    def testNoneYamlRaises( self ) :
        expectedRootDirectory = '.'
        with self.assertRaisesRegex( YamlNotFound, '^No package-manifest YAML data present' ) :
            Manifest.from_yamlData( None, expectedRootDirectory )


    def testEmptyDictYamlRaises( self ) :
        expectedRootDirectory = '.'
        with self.assertRaisesRegex( YamlNotFound, '^No package-manifest YAML data present' ) :
            Manifest.from_yamlData( dict(), expectedRootDirectory )


    def testEmptyListYamlRaises( self ) :
        expectedRootDirectory = '.'
        with self.assertRaisesRegex( YamlNotFound, '^No package-manifest YAML data present' ) :
            Manifest.from_yamlData( list(), expectedRootDirectory )


    def testDecodeOperationsList( self ) :
        expectedRootDirectory = '.'

        inputYamlData = [
            { 'global-include' :
                  { 'files' :
                        [ '*.h' ] }, },
            { 'exclude' :
                  { 'files' :
                        [ 'LICENSE', 'README' ] }, },
            { 'prune' :
                  { 'directory' : 'bin' }, },
        ]

        manifestUnderTest = Manifest.from_yamlData( inputYamlData, expectedRootDirectory )

        self.assertEqual( expectedRootDirectory, manifestUnderTest.pathSet.rootDirectory )

        self.assertEqual( 4, len( manifestUnderTest.operations ) )

        self.assertTrue( isinstance( manifestUnderTest.operations[ 0 ], GlobalInclude ) )
        self.assertTrue( isinstance( manifestUnderTest.operations[ 1 ], LocalExclude ) )
        self.assertTrue( isinstance( manifestUnderTest.operations[ 2 ], LocalExclude ) )
        self.assertTrue( isinstance( manifestUnderTest.operations[ 3 ], Prune ) )


if __name__ == '__main__' :
    unittest.main()
