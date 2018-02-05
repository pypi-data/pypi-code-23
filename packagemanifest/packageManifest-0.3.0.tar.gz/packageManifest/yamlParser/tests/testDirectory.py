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

from ..directory import \
    Directory, \
    YamlNotFound


class TestYamlDirectory( unittest.TestCase ) :
    def testNoneNotFound( self ) :
        yamlData = None

        with self.assertRaisesRegex( YamlNotFound, '^yamlData is None' ) :
            Directory.from_yamlData( yamlData )


    def testNotDirectoryNotFound( self ) :
        yamlData = { 'files' : [ 'one', 'two' ] }

        with self.assertRaisesRegex( YamlNotFound, '^directory not specified in yaml' ) :
            Directory.from_yamlData( yamlData )


    def testPathOk( self ) :
        expectedPath = 'path'
        yamlData = { 'directory' : expectedPath }

        directoryUnderTest = Directory.from_yamlData( yamlData )

        self.assertEqual( expectedPath, directoryUnderTest.path )


if __name__ == '__main__' :
    unittest.main()
