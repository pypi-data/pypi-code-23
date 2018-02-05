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

from ..exclude import \
    Exclude, \
    YamlNotFound


class TestGlobalNameYamlExclude( unittest.TestCase ) :
    def testNoneNotFound( self ) :
        yamlData = None

        with self.assertRaisesRegex( YamlNotFound, '^yamlData is None' ) :
            Exclude.from_yamlData( yamlData )


    def testExcludeNotFound( self ) :
        yamlData = { 'files' : [ 'one' ] }

        with self.assertRaisesRegex( YamlNotFound, '^global-exclude not found in yaml data' ) :
            Exclude.from_yamlData( yamlData )


    def testExcludeFilesNotFound( self ) :
        yamlData = { 'global-exclude' : { 'directory' : 'one' } }

        with self.assertRaisesRegex( YamlNotFound, '^global-exclude must use files directive' ) :
            Exclude.from_yamlData( yamlData )


    def testExcludeOk( self ) :
        expectedPatterns = [ 'one', 't*' ]
        yamlData = { 'global-exclude' : { 'files' : expectedPatterns } }

        excludesUnderTest = Exclude.from_yamlData( yamlData )

        self.assertTrue( isinstance( excludesUnderTest, list ) )
        self.assertEqual( len( expectedPatterns ), len( excludesUnderTest ) )
        self.assertEqual( expectedPatterns[ 0 ], excludesUnderTest[ 0 ].excludePattern )
        self.assertEqual( expectedPatterns[ 1 ], excludesUnderTest[ 1 ].excludePattern )


if __name__ == '__main__' :
    unittest.main()
