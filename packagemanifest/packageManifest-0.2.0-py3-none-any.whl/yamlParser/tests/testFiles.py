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

from ..files import \
    Files, \
    YamlNotFound


class TestYamlFiles( unittest.TestCase ) :
    def testNoneNotFound( self ) :
        yamlData = None

        with self.assertRaisesRegex( YamlNotFound, '^yamlData is None' ) :
            Files.from_yamlData( yamlData )


    def testNotDirectoryNotFound( self ) :
        yamlData = { 'directory' : 'one' }

        with self.assertRaisesRegex( YamlNotFound, '^files not specified in yaml' ) :
            Files.from_yamlData( yamlData )

    def testNonListPattern( self ):
        yamlData = { 'files' : 'one' }

        with self.assertRaisesRegex( YamlNotFound, '^files patterns must be a list' ) :
            Files.from_yamlData( yamlData )


    def testPatternsOk( self ) :
        expectedPatterns = [ 'one', 't*' ]
        yamlData = { 'files' : expectedPatterns }

        filesUnderTest = Files.from_yamlData( yamlData )

        self.assertEqual( expectedPatterns, filesUnderTest.patterns )


if __name__ == '__main__' :
    unittest.main()
