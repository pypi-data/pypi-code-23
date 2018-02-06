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


class PackageTestData :
    subdirFoundCount = 0
    notFoundFileCount = 0

    addedFiles = set()


    def __init__( self ) :
        self.filesToPackage = {
            os.path.join( 'some', 'file' ),
            os.path.join( 'afile' ),
            os.path.join( 'some', 'subdir', 'file' ),
            os.path.join( 'some', 'subdir' ),
            os.path.join( 'notFound' ),
        }

        self.expectedPackagedFiles = {
            os.path.join( 'some', 'file' ),
            os.path.join( 'afile' ),
            os.path.join( 'some', 'subdir', 'file' ),
        }

        PackageTestData.subdirFoundCount = 0
        PackageTestData.notFoundFileCount = 0
        PackageTestData.addedFiles = set()


    @staticmethod
    def mockOsExists( filename ) :
        if filename == 'notFound' :
            return False
        else :
            return True


    @staticmethod
    def mockOsIsfile( filename ) :
        if filename == os.path.join( 'some', 'subdir' ) :
            PackageTestData.subdirFoundCount += 1

            return False
        elif filename == 'notFound' :
            PackageTestData.notFoundFileCount += 1

            return False
        else :
            return True


    @staticmethod
    def mockTarFileAdd( name ) :
        PackageTestData.addedFiles.add( name )
