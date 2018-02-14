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


class TestZipPackage( unittest.TestCase ) :
    def testDefaultDisabledPackage( self ) :
        packageOptions = parseArguments( list() )

        self.assertFalse( packageOptions.isZipFile )


    def testShortEnabledPackage( self ) :
        expectedPackage = 'distribution-out.zip'

        packageOptions = parseArguments( [ '-z' ] )

        self.assertTrue( packageOptions.isZipFile )
        actualPackage = os.path.basename( packageOptions.zipPackagePath )
        self.assertEqual( expectedPackage, actualPackage )


    def testLongEnabledPackage( self ) :
        expectedPackage = 'distribution-out.zip'

        packageOptions = parseArguments( [ '--zip' ] )

        self.assertTrue( packageOptions.isTarFile )
        actualPackage = os.path.basename( packageOptions.zipPackagePath )
        self.assertEqual( expectedPackage, actualPackage )


if __name__ == '__main__' :
    unittest.main()
