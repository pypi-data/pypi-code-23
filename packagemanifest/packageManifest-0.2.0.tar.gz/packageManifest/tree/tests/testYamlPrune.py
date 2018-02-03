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

from ..prune import \
    Prune, \
    YamlNotFound


class TestYamlPrune( unittest.TestCase ) :
    def testNoneNotFound( self ) :
        yamlData = None

        with self.assertRaisesRegex( YamlNotFound, '^yamlData is None' ) :
            Prune.from_yamlData( yamlData )


    def testPruneNotFound( self ) :
        yamlData = { 'files' : [ 'one' ] }

        with self.assertRaisesRegex( YamlNotFound, '^prune not found in yaml data' ) :
            Prune.from_yamlData( yamlData )


    def testPruneDirectoryNotFound( self ) :
        yamlData = { 'prune' : { 'files' : [ 'one' ] } }

        with self.assertRaisesRegex( YamlNotFound, '^prune must use directory directive' ) :
            Prune.from_yamlData( yamlData )


    def testPruneOk( self ) :
        expectedDirectory = 'subdir'

        yamlData = { 'prune' :
            {
                'directory' : expectedDirectory,
            },
        }

        pruneUnderTest = Prune.from_yamlData( yamlData )

        self.assertEqual( 1, len( pruneUnderTest ) )
        self.assertEqual( expectedDirectory, pruneUnderTest[ 0 ].directory )


if __name__ == '__main__' :
    unittest.main()
