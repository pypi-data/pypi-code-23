#
# Copyright 2018 Russell Smiley
#
# This file is part of packager.
#
# packager is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# packager is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with packager.  If not, see <http://www.gnu.org/licenses/>.
#

import unittest

from ..arguments import parseArguments


class TestAppendArgument( unittest.TestCase ) :
    def testDefault( self ) :
        expectedValue = False

        packageOptions = parseArguments( list() )

        actualValue = packageOptions.append

        self.assertEqual( expectedValue, actualValue )


    def testGoodValue( self ) :
        expectedValue = True

        packageOptions = parseArguments( [ '--append' ] )

        actualValue = packageOptions.append

        self.assertEqual( expectedValue, actualValue )


if __name__ == '__main__' :
    unittest.main()
