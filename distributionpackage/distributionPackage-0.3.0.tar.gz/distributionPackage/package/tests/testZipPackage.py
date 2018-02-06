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

import unittest.mock

from .utility import PackageTestData

from ..zipPackage import \
    ZipPackage, \
    zipfile


class TestZipPackage( unittest.TestCase ) :
    def setUp( self ) :
        self.data = PackageTestData()


    def testNonExistentFileIsDiscovered( self ) :
        expectedNotFoundCount = 1

        mockZipFile = unittest.mock.create_autospec( zipfile.ZipFile )

        with unittest.mock.patch( 'os.path.isfile', side_effect = PackageTestData.mockOsIsfile ) as mockOsIsfile :
            with unittest.mock.patch( 'os.path.exists', side_effect = PackageTestData.mockOsExists ) as mockOsExists :
                with unittest.mock.patch.object( ZipPackage, '_ZipPackage__createZipfile', return_value = mockZipFile ) as mockZipPackage:
                    packageUnderTest = ZipPackage( self.id(), '.' )

                    packageUnderTest.build( self.data.filesToPackage )

        self.assertEqual( expectedNotFoundCount, self.data.notFoundFileCount )


    def testSubdirIsDiscovered( self ) :
        expectedSubdirFoundCount = 1

        mockZipFile = unittest.mock.create_autospec( zipfile.ZipFile )

        with unittest.mock.patch( 'os.path.isfile', side_effect = PackageTestData.mockOsIsfile ) as mockOsIsfile :
            with unittest.mock.patch( 'os.path.exists', side_effect = PackageTestData.mockOsExists ) as mockOsExists :
                with unittest.mock.patch.object( ZipPackage, '_ZipPackage__createZipfile', return_value = mockZipFile ) as mockZipPackage:
                    packageUnderTest = ZipPackage( self.id(), '.' )

                    packageUnderTest.build( self.data.filesToPackage )

        self.assertEqual( expectedSubdirFoundCount, self.data.subdirFoundCount )


    def testAddedFiles( self ) :
        mockZipFile = unittest.mock.create_autospec( zipfile.ZipFile )

        mockZipFile.write.side_effect = PackageTestData.mockTarFileAdd

        with unittest.mock.patch( 'os.path.isfile', side_effect = PackageTestData.mockOsIsfile ) as mockOsIsfile :
            with unittest.mock.patch( 'os.path.exists', side_effect = PackageTestData.mockOsExists ) as mockOsExists :
                with unittest.mock.patch.object( ZipPackage, '_ZipPackage__createZipfile', return_value = mockZipFile ) as mockZipPackage:
                    packageUnderTest = ZipPackage( self.id(), '.' )

                    packageUnderTest.build( self.data.filesToPackage )

        self.assertEqual( self.data.expectedPackagedFiles, PackageTestData.addedFiles )


if __name__ == '__main__' :
    unittest.main()
