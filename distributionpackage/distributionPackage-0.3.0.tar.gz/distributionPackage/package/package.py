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

from .tarPackage import TarPackage
from .zipPackage import ZipPackage


class Package :
    def __init__( self, manifest, packageOptions ) :
        self.manifest = manifest
        self.packageOptions = packageOptions
        self.packages = list()


    def build( self ) :
        if self.packageOptions.isZipFile :
            package = ZipPackage( self.packageOptions.zipPackagePath, self.packageOptions.projectRoot )
            self.packages.append( package )

        if self.packageOptions.isTarFile :
            package = TarPackage( self.packageOptions.tarPackagePath, self.packageOptions.projectRoot )
            self.packages.append( package )

        filesToPackage = self.manifest.apply()
        for thisPackage in self.packages :
            thisPackage.build( filesToPackage )
