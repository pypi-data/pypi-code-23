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

from ..include import \
    Include, \
    YamlNotFound


class TestRecursiveYamlInclude( unittest.TestCase ) :
    def testNoneNotFound( self ) :
        yamlData = None

        with self.assertRaisesRegex( YamlNotFound, '^yamlData is None' ) :
            Include.from_yamlData( yamlData )


    def testIncludeNotFound( self ) :
        yamlData = { 'files' : [ 'one' ] }

        with self.assertRaisesRegex( YamlNotFound, '^recursive-include not found in yaml data' ) :
            Include.from_yamlData( yamlData )


    def testIncludeFilesNotFound( self ) :
        yamlData = { 'recursive-include' : { 'directory' : 'one' } }

        with self.assertRaisesRegex( YamlNotFound, '^recursive-include must use files and directory directives' ) :
            Include.from_yamlData( yamlData )


    def testIncludeDirectoryNotFound( self ) :
        yamlData = { 'recursive-include' : { 'files' : [ 'one' ] } }

        with self.assertRaisesRegex( YamlNotFound, '^recursive-include must use files and directory directives' ) :
            Include.from_yamlData( yamlData )


    def testIncludeOk( self ) :
        expectedDirectory = 'subdir'
        expectedPatterns = [ 'one', 't*' ]

        yamlData = { 'recursive-include' :
            {
                'directory' : expectedDirectory,
                'files' : expectedPatterns,
            },
        }

        includesUnderTest = Include.from_yamlData( yamlData )

        self.assertTrue( isinstance( includesUnderTest, list ) )

        self.assertEqual( len( expectedPatterns ), len( includesUnderTest ) )
        self.assertEqual( expectedPatterns[ 0 ], includesUnderTest[ 0 ].includePattern )
        self.assertEqual( expectedPatterns[ 1 ], includesUnderTest[ 1 ].includePattern )

        self.assertEqual( expectedDirectory, includesUnderTest[ 0 ].directory )
        self.assertEqual( expectedDirectory, includesUnderTest[ 1 ].directory )


if __name__ == '__main__' :
    unittest.main()
