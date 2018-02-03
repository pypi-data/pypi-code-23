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
    Files, \
    YamlNotFound

from .include import applyGlobalInclusions


def applyGlobalExclusions( pathNames, exclusions ) :
    """
    Apply unix glob wildcard expressions to select items from an iterable of file names (basename). The wildcard is applied
    "globally".

    eg.
      "*.py" implies "exclude *.py files anywhere in the root directory and it's subdirectories, recursively".

    :param pathNames: path names to be filtered expressed relative to the root directory of the package-manifest.
    :param exclusions: exclude patterns

    :return: set of path names after exclusions have been applied.
    """
    includedPaths = applyGlobalInclusions( pathNames, exclusions )

    retainedPaths = set( pathNames ) - includedPaths

    return retainedPaths


class Exclude( PathOperation ) :
    __yamlKey = 'global-exclude'


    def __init__( self, excludePattern ) :
        self.excludePattern = excludePattern


    def apply( self, originalPathNames, currentPathNames ) :
        assert all( [ x in originalPathNames for x in currentPathNames ] )

        retainedPaths = applyGlobalExclusions( originalPathNames, [ self.excludePattern ] )
        modifiedNames = currentPathNames & retainedPaths

        return modifiedNames


    @classmethod
    def from_yamlData( cls, yamlData ) :
        if yamlData is None :
            raise YamlNotFound( 'yamlData is None' )
        elif Exclude.__yamlKey not in yamlData :
            raise YamlNotFound( '{1} not found in yaml data, {0}'.format( yamlData, Exclude.__yamlKey ) )
        else :
            try :
                filePatterns = Files.from_yamlData( yamlData[ Exclude.__yamlKey ] )

                result = list()
                for thisPattern in filePatterns.patterns :
                    result.append( cls( thisPattern ) )
            except YamlNotFound as e :
                raise YamlNotFound( '{1} must use files directive, {0}'.format( yamlData, Exclude.__yamlKey ) ) from e

        return result
