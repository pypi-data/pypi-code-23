#
# Copyright 2018 Russell Smiley
#
# This file is part of distributionPackage.
#
# distributionPackage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# distributionPackage is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with distributionPackage.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import unittest

from ..arguments import parseArguments


class MyTestOutputArgument( unittest.TestCase ) :
    def testDefaultOutput( self ) :
        expectedDefaultOutput = '.'

        packageOptions = parseArguments( list() )

        actualPath = packageOptions.tarPackagePath

        actualOutput = os.path.dirname( actualPath )

        self.assertEqual( expectedDefaultOutput, actualOutput )


    def testShortFormOutput( self ) :
        expectedOutput = os.path.join( 'some', 'path' )

        packageOptions = parseArguments( [ '-o', expectedOutput ] )

        actualPath = packageOptions.tarPackagePath

        actualOutput = os.path.dirname( actualPath )

        self.assertEqual( expectedOutput, actualOutput )


    def testLongFormOutput( self ) :
        expectedOutput = os.path.join( 'some', 'path' )

        packageOptions = parseArguments( [ '--output', expectedOutput ] )

        actualPath = packageOptions.tarPackagePath

        actualOutput = os.path.dirname( actualPath )

        self.assertEqual( expectedOutput, actualOutput )


if __name__ == '__main__' :
    unittest.main()
