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
import logging
import zipfile

from .base import PackageBase
from .directory import ChangeDirectory
from .interface import PackageInterface


log = logging.getLogger( __name__ )


class ZipPackage( PackageInterface, PackageBase ) :
    def __init__( self, fileName, projectRoot, append ) :
        super().__init__( fileName, projectRoot, append )

        self.zipFile = None


    def build( self, filesToPackage ) :
        if self.append :
            self.zipFile = self.__openForAppend()
        else :
            self.zipFile = self.__openForWrite()

        self.__doBuild( filesToPackage )


    def __openForAppend( self ) :
        if os.path.isfile( self.fileName ) :
            log.info( 'Appending to existing file, {0}'.format( self.fileName ) )
            openedZip = zipfile.ZipFile( self.fileName,
                                         mode = 'a' )
        elif not os.path.exists( self.fileName ) :
            # File doesn't exist so just do a normal write.
            openedZip = self.__openForWrite()
        else :
            # File exists, but is not a file. So just exit.
            raise RuntimeError( 'Filename exists but is not a file, {0}'.format( self.fileName ) )

        return openedZip


    def __openForWrite( self ) :
        openedZip = zipfile.ZipFile( self.fileName,
                                     mode = 'w' )

        return openedZip


    def __doBuild( self, filesToPackage ) :
        with ChangeDirectory( self.projectRoot ) :
            for thisFile in filesToPackage :
                if os.path.isfile( thisFile ) :
                    self.zipFile.write( thisFile )
                elif not os.path.exists( thisFile ) :
                    realFileName = os.path.realpath( os.path.abspath( os.path.join( self.projectRoot, thisFile ) ) )

                    log.warning( 'File to package does not exist, {0}'.format( realFileName ) )
