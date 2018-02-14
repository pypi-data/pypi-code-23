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

from ..tarPackage import \
    TarPackage, \
    tarfile

import distributionPackage.package.tarPackage


class TestTarPackage( unittest.TestCase ) :
    def setUp( self ) :
        self.data = PackageTestData()


    def testAppendDisabledCreatesNonexistentFile( self ) :
        appendMode = False
        mockTarFile = unittest.mock.create_autospec( tarfile.TarFile )

        with unittest.mock.patch( 'tarfile.open', return_value = mockTarFile ) as mockTarOpen :
            with unittest.mock.patch(
                    'distributionPackage.package.tarPackage.TarPackage._TarPackage__doBuild' ) as mock_doBuild :
                packageUnderTest = TarPackage( self.id(), '.', appendMode )

                packageUnderTest.build( self.data.filesToPackage )

        mockTarOpen.assert_called_with( name = self.id(),
                                        mode = 'w:gz' )


    def testNonExistentFileIsDiscovered( self ) :
        expectedNotFoundCount = 1

        mockTarFile = unittest.mock.create_autospec( tarfile.TarFile )

        with unittest.mock.patch( 'os.path.isfile', side_effect = PackageTestData.mockOsIsfile ) as mockOsIsfile :
            with unittest.mock.patch( 'os.path.exists', side_effect = PackageTestData.mockOsExists ) as mockOsExists :
                with unittest.mock.patch( 'tarfile.open', return_value = mockTarFile ) as mockTarOpen :
                    packageUnderTest = TarPackage( self.id(), '.', False )

                    packageUnderTest.build( self.data.filesToPackage )

        self.assertEqual( expectedNotFoundCount, self.data.notFoundFileCount )


    def testSubdirIsDiscovered( self ) :
        expectedSubdirFoundCount = 1

        mockTarFile = unittest.mock.create_autospec( tarfile.TarFile )

        with unittest.mock.patch( 'os.path.isfile', side_effect = PackageTestData.mockOsIsfile ) as mockOsIsfile :
            with unittest.mock.patch( 'os.path.exists', side_effect = PackageTestData.mockOsExists ) as mockOsExists :
                with unittest.mock.patch( 'tarfile.open', return_value = mockTarFile ) as mockTarOpen :
                    packageUnderTest = TarPackage( self.id(), '.', False )

                    packageUnderTest.build( self.data.filesToPackage )

        self.assertEqual( expectedSubdirFoundCount, self.data.subdirFoundCount )


    def testAddedFiles( self ) :
        mockTarFile = unittest.mock.create_autospec( tarfile.TarFile )

        mockTarFile.add.side_effect = PackageTestData.mockFileAdd

        with unittest.mock.patch( 'os.path.isfile', side_effect = PackageTestData.mockOsIsfile ) as mockOsIsfile :
            with unittest.mock.patch( 'os.path.exists', side_effect = PackageTestData.mockOsExists ) as mockOsExists :
                with unittest.mock.patch( 'tarfile.open', return_value = mockTarFile ) as mockTarOpen :
                    packageUnderTest = TarPackage( self.id(), '.', False )

                    packageUnderTest.build( self.data.filesToPackage )

        self.assertEqual( self.data.expectedPackagedFiles, PackageTestData.addedFiles )


class TestTarPackageAppendMode( unittest.TestCase ) :
    def setUp( self ) :
        self.data = PackageTestData()


    def testAppendCreatesNonexistentFile( self ) :
        appendMode = True
        mockTarFile = unittest.mock.create_autospec( tarfile.TarFile )

        with unittest.mock.patch( 'tarfile.open', return_value = mockTarFile ) as mockTarOpen :
            with unittest.mock.patch( 'gzip.open', autospec = True ) as mockGzipOpen :
                with unittest.mock.patch( 'os.path.isfile', return_value = True ) as mockOsIsfile :
                    with unittest.mock.patch(
                            'distributionPackage.package.tarPackage.TarPackage._TarPackage__doBuild' ) as mock_doBuild :
                        packageUnderTest = TarPackage( self.id(), '.', appendMode )

                        packageUnderTest.build( self.data.filesToPackage )

                        mockTarOpen.assert_called_with( fileobj = packageUnderTest.gzipFile,
                                                        mode = 'a' )


    def testAppendToFile( self ) :
        appendMode = True
        mockTarFile = unittest.mock.create_autospec( tarfile.TarFile )

        with unittest.mock.patch( 'tarfile.open', return_value = mockTarFile ) as mockTarOpen :
            with unittest.mock.patch( 'os.path.isfile', return_value = False ) as mockOsIsfile :
                with unittest.mock.patch(
                        'distributionPackage.package.tarPackage.TarPackage._TarPackage__doBuild' ) as mock_doBuild :
                    packageUnderTest = TarPackage( self.id(), '.', appendMode )

                    packageUnderTest.build( self.data.filesToPackage )

                    mockTarOpen.assert_called_with( name = self.id(),
                                                    mode = 'w:gz' )


    def testExistentNonFileRaises( self ) :
        appendMode = True
        mockTarFile = unittest.mock.create_autospec( tarfile.TarFile )

        with unittest.mock.patch( 'tarfile.open', return_value = mockTarFile ) as mockTarOpen :
            with unittest.mock.patch( 'os.path.isfile', return_value = False ) as mockOsIsfile :
                with unittest.mock.patch( 'os.path.exists', return_value = True ) as mockOsIsfile :
                    with unittest.mock.patch(
                            'distributionPackage.package.tarPackage.TarPackage._TarPackage__doBuild' ) as mock_doBuild :
                        packageUnderTest = TarPackage( self.id(), '.', appendMode )

                        with self.assertRaisesRegex( RuntimeError, '^Filename exists but is not a file' ) :
                            packageUnderTest.build( self.data.filesToPackage )


if __name__ == '__main__' :
    unittest.main()
