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


class TestTarArgument( unittest.TestCase ) :
    def testDefaultTarPackage( self ) :
        expectedDefaultPackage = 'distribution-out.tar.gz'

        packageOptions = parseArguments( list() )

        actualPackage = os.path.basename( packageOptions.tarPackagePath )
        self.assertEqual( expectedDefaultPackage, actualPackage )
        self.assertTrue( packageOptions.isTarFile )


    def testShortDisabledPackage( self ) :
        packageOptions = parseArguments( [ '-n' ] )

        self.assertFalse( packageOptions.isTarFile )
        self.assertIsNone( packageOptions.tarPackagePath )


    def testLongDisabledPackage( self ) :
        packageOptions = parseArguments( [ '--no-tar' ] )

        self.assertFalse( packageOptions.isTarFile )
        self.assertIsNone( packageOptions.tarPackagePath )


if __name__ == '__main__' :
    unittest.main()
