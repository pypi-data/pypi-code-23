#
# Copyright 2017 Russell Smiley
#
# This file is part of package-manifest.
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

from ..exclude import applyExclusions


class TestApplyExclusions( unittest.TestCase ) :
    def testSimpleExclude( self ) :
        exclusions = [ 't*' ]
        inputList = [ 'one', 'two', 'three', 'four' ]
        expectedList = { 'one', 'four' }

        actualList = set( applyExclusions( inputList, exclusions ) )

        self.assertEqual( actualList, expectedList )


    def testExcludeTwoWildcards( self ) :
        exclusions = [ 'tw*', 'th*' ]
        inputList = [ 'one', 'two', 'three', 'four' ]
        expectedList = { 'one', 'four' }

        actualList = set( applyExclusions( inputList, exclusions ) )

        self.assertEqual( actualList, expectedList )


    def testPathExclusion( self ) :
        exclusions = [ 'two' ]
        inputList = [ 'one', 'two', 'three/two', 'four' ]
        expectedList = { 'one', 'three/two', 'four' }

        actualList = set( applyExclusions( inputList, exclusions ) )

        self.assertEqual( actualList, expectedList )


    def testPathExclusion2( self ) :
        exclusions = [ 'one/two' ]
        inputList = [ 'one/two', 'one/two/three', 'four' ]
        expectedList = { 'one/two/three', 'four' }

        actualList = set( applyExclusions( inputList, exclusions ) )

        self.assertEqual( actualList, expectedList )


    def testPathExclusion3( self ) :
        exclusions = [ 'one/two*' ]
        inputList = [ 'one/two', 'one/two/three', 'four' ]
        expectedList = { 'four' }

        actualList = set( applyExclusions( inputList, exclusions ) )

        self.assertEqual( actualList, expectedList )


if __name__ == '__main__' :
    unittest.main()
