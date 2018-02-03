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

from ..path.path import PathOperation

from ..yamlParser import \
    Directory, \
    YamlNotFound

from .graft import graftPaths


def prunePaths( pathNames, directory ) :
    """
    Prune (remove) a directory and it's files, recursively, from the set of input paths.

    :param pathNames: Iterable of paths from which to select files in directory.
    :param directory: Directory to select pruned files from relative to the package-manifest root directory.

    :return: set of filtered files
    """
    graftedPaths = graftPaths( pathNames, directory )

    prunedPaths = set( pathNames ) - graftedPaths

    return prunedPaths


class Prune( PathOperation ) :
    __yamlKey = 'prune'


    def __init__( self, directory ) :
        self.directory = directory


    def apply( self, originalPathNames, currentPathNames ) :
        assert all( [ x in originalPathNames for x in currentPathNames ] )

        retainedPaths = prunePaths( originalPathNames, self.directory )
        modifiedPaths = currentPathNames & retainedPaths

        return modifiedPaths


    @classmethod
    def from_yamlData( cls, yamlData ) :
        if yamlData is None :
            raise YamlNotFound( 'yamlData is None' )
        elif Prune.__yamlKey not in yamlData :
            raise YamlNotFound( '{1} not found in yaml data, {0}'.format( yamlData, Prune.__yamlKey ) )
        else :
            try :
                directory = Directory.from_yamlData( yamlData[ Prune.__yamlKey ] )

                # Need to return a list even though there is only one element in order to maintain compatibility with
                # the local, global & recursive operations.
                result = [ cls( directory.path ) ]
            except YamlNotFound as e :
                raise YamlNotFound(
                    '{1} must use directory directive, {0}'.format( yamlData, Prune.__yamlKey ) ) from e

        return result
