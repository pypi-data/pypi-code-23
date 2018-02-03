#
# Copyright 2018 Russell Smiley
#
# This file is part of package-manifest.
#
# package-manifest is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# package-manifest is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with package-manifest.  If not, see <http://www.gnu.org/licenses/>.
#

import os

from .path import makeRelativePaths


class PathSet :
    def __init__( self, rootDirectory ) :
        self.pathNames = set()
        self.rootDirectory = rootDirectory

        if not os.path.isdir( self.rootDirectory ) :
            raise RuntimeError( 'Manifest root directory does not exist, ' + repr( self.rootDirectory ) )

        self.__buildOriginalFiles()


    def __buildOriginalFiles( self ) :
        # Recursively acquire all files/folders in the root directory.
        for root, directories, files in os.walk( self.rootDirectory ) :
            for thisDir in directories :
                self.pathNames.add( os.path.join( root, thisDir ) )

            for thisFile in files :
                self.pathNames.add( os.path.join( root, thisFile ) )

        self.__makeFilesRelative()


    def __makeFilesRelative( self ) :
        self.pathNames = makeRelativePaths( self.pathNames, self.rootDirectory )
