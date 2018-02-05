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

import unittest

from ..path import makeRelativePaths


class TestMakeRelativePaths( unittest.TestCase ) :
    def testGoodValues( self ) :
        rootPath = '/some/path'
        inputList = [
            '/some/path/file1',
            '/some/path/file2',
            '/some/path/subdir/file3',
        ]
        expectedPaths = [
            'file1',
            'file2',
            'subdir/file3',
        ]

        actualPaths = makeRelativePaths( inputList, rootPath )

        self.assertEqual( actualPaths, expectedPaths )


if __name__ == '__main__' :
    unittest.main( )
