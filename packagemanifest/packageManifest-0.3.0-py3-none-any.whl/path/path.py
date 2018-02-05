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

import abc
import os.path
import re


def filterNotInDirectory( pathNames, directory ) :
    """
    Remove paths from an iterable of path names that are not recursively "inside" the specified directory.

    :param pathNames: iterable of paths.
    :param directory: directory path.

    :return: list of paths inside `directory`.
    """
    relativeNames = makeRelativePaths( pathNames, directory )

    currentDirNames = list()
    for thisName in relativeNames :
        if re.match( r'^\.\.', thisName ) is None :
            currentDirNames.append( thisName )

    return prependDirectory( directory, currentDirNames )


def makeRelativePaths( paths, pathRoot ) :
    """
    Turn an iterable of paths and express them as relative to the specified root directory path using `os.path.relpath`.

    Assumes that `paths` are valid for use with `os.path.relpath` against `pathRoot`.

    :param paths: iterable of paths
    :param pathRoot: directory path stem of paths

    :return: list of resulting relative paths.
    """
    relativePaths = [ os.path.relpath( x, pathRoot ) for x in paths ]
    return relativePaths


def prependDirectory( directory, names ) :
    """
    Prepend directory path to an iterable of path names.

    :param directory: directory path to be prepended to names
    :param names: iterable of names

    :return: list of prepended names.
    """
    return [ os.path.normpath( os.path.join( directory, x ) ) for x in names ]


class PathOperation( metaclass = abc.ABCMeta ) :
    @abc.abstractmethod
    def apply( self, originalPathNames, currentPathNames ) :
        """
        Apply a path operation to a set of path names.

        :param originalPathNames: The original list of all path names
        :param currentPathNames: The current list of path names, perhaps as processed by other (previous) path operations.

        :return: Modified currentPathNames combining this path operation with the effects of previous path operations.
        """
        pass
