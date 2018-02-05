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

from .exception import YamlNotFound


class Directory :
    def __init__( self ) :
        self.path = None


    @classmethod
    def from_yamlData( cls, yamlData ) :
        if yamlData is None :
            raise YamlNotFound( 'yamlData is None' )
        elif 'directory' not in yamlData :
            raise YamlNotFound( 'directory not specified in yaml, {0}'.format( yamlData ) )
        else :
            thisDirectory = cls()

            thisDirectory.path = yamlData[ 'directory' ]

        return thisDirectory
