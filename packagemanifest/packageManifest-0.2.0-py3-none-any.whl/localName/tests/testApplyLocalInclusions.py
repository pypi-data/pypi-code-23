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

from ..include import applyInclusions


class TestLocalApplyInclusions( unittest.TestCase ) :
    def functionUnderTest( self, inputList, inclusions ) :
        return applyInclusions( inputList, inclusions )


    def testSimpleInclude( self ) :
        inclusions = [ 't*' ]
        inputList = [ 'one', 'two', 'three', 'four' ]
        expectedList = { 'two', 'three' }

        actualList = set( self.functionUnderTest( inputList, inclusions ) )

        self.assertEqual( actualList, expectedList )


    def testIncludeTwoWildcards( self ) :
        inclusions = [ 'tw*', 'th*' ]
        inputList = [ 'one', 'two', 'three', 'four' ]
        expectedList = { 'two', 'three' }

        actualList = set( self.functionUnderTest( inputList, inclusions ) )

        self.assertEqual( actualList, expectedList )


    def testIncludePathWildcards( self ) :
        inclusions = [ 'one/tw*' ]
        inputList = [ 'one', 'one/twill', 'two', 'three', 'one/two', 'four' ]
        expectedList = { 'one/two', 'one/twill' }

        actualList = set( self.functionUnderTest( inputList, inclusions ) )

        self.assertEqual( actualList, expectedList )


    def testSubdirInclude( self ) :
        inclusions = [ 't*' ]
        inputList = [ 'one', 'two', 'three', 'four', 'subdir/one', 'subdir/two' ]
        expectedList = { 'two', 'three' }

        actualList = set( self.functionUnderTest( inputList, inclusions ) )

        self.assertEqual( actualList, expectedList )


if __name__ == '__main__' :
    unittest.main()
