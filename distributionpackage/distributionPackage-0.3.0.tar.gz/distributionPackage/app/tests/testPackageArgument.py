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
import re
import unittest

from ..arguments import parseArguments


class TestPackageArgument( unittest.TestCase ) :
    def testDefaultPackage( self ) :
        expectedDefaultPackage = 'distribution-out'

        packageOptions = parseArguments( list() )

        tarPath = packageOptions.tarPackagePath

        actualPackageFile = os.path.basename( tarPath )

        self.assertIsNotNone( re.search( '^{0}'.format( expectedDefaultPackage ), actualPackageFile ) )


    def testShortFormPackage( self ) :
        expectedPackage = 'my-package'

        packageOptions = parseArguments( [ '-p', expectedPackage ] )

        tarPath = packageOptions.tarPackagePath

        actualPackageFile = os.path.basename( tarPath )

        self.assertIsNotNone( re.search( '^{0}'.format( expectedPackage ), actualPackageFile ) )


    def testLongFormPackage( self ) :
        expectedPackage = 'my-package'

        packageOptions = parseArguments( [ '--package', expectedPackage ] )

        tarPath = packageOptions.tarPackagePath

        actualPackageFile = os.path.basename( tarPath )

        self.assertIsNotNone( re.search( '^{0}'.format( expectedPackage ), actualPackageFile ) )


if __name__ == '__main__' :
    unittest.main()
