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

from ..include import applyGlobalInclusions


class TestGlobalInclusions( unittest.TestCase ) :
    def testGlobalSubdirInclude( self ) :
        inclusions = [ 't*' ]
        inputList = [ 'one', 'two', 'three', 'four', 'subdir/one', 'subdir/two' ]
        expectedList = { 'two', 'three', 'subdir/two' }

        actualList = set( applyGlobalInclusions( inputList, inclusions ) )

        self.assertEqual( expectedList, actualList )


    def testGlobalSubdirPathInclude( self ) :
        inclusions = [ 'subdir/t*' ]
        inputList = [ 'one', 'two', 'three', 'four', 'subdir/one', 'subdir/two', 'another/subdir/twice' ]
        expectedList = { 'subdir/two', 'another/subdir/twice' }

        actualList = set( applyGlobalInclusions( inputList, inclusions ) )

        self.assertEqual( expectedList, actualList )


if __name__ == '__main__' :
    unittest.main()
