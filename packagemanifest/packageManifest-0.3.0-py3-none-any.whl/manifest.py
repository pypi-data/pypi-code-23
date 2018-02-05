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

import logging
import yaml

from .globalName import Include as GlobalInclude
from .globalName import Exclude as GlobalExclude
from .localName import Include as LocalInclude
from .localName import Exclude as LocalExclude
from .recursive import Include as RecursiveInclude
from .recursive import Exclude as RecursiveExclude
from .tree import \
    Graft, \
    Prune

from .path import PathSet

from .yamlParser import YamlNotFound


log = logging.getLogger( __name__ )


class Manifest :
    __operationYamlParsers = [
        GlobalExclude.from_yamlData,
        GlobalInclude.from_yamlData,
        LocalExclude.from_yamlData,
        LocalInclude.from_yamlData,
        RecursiveExclude.from_yamlData,
        RecursiveInclude.from_yamlData,
        Graft.from_yamlData,
        Prune.from_yamlData,
    ]


    def __init__( self,
                  rootDirectory = None,
                  pathSet = None ) :
        assert (rootDirectory is not None) ^ (pathSet is not None)

        if rootDirectory is not None :
            self.pathSet = PathSet( rootDirectory )
        elif pathSet is not None :
            assert hasattr( pathSet, 'pathNames' )

            self.pathSet = pathSet

        self.operations = list()


    def apply( self ) :
        processedFiles = set()
        for thisOperation in self.operations :
            processedFiles = thisOperation.apply( self.pathSet.pathNames, processedFiles )

        return processedFiles


    @classmethod
    def from_yamlData( cls, yamlData, rootDirectory ) :
        if not yamlData :
            raise YamlNotFound( 'No package-manifest YAML data present' )

        thisManifest = cls( rootDirectory = rootDirectory )

        for thisElement in yamlData :
            isValidOperationYaml = False
            for thisParser in cls.__operationYamlParsers :
                try :
                    operation = thisParser( thisElement )
                    thisManifest.operations += operation

                    isValidOperationYaml = True
                except YamlNotFound as e :
                    isValidOperationYaml |= False

                    log.debug( repr( e ) )

        if not isValidOperationYaml :
            raise YamlNotFound( 'No valid operations found in YAML element, {0}'.format( thisElement ) )

        return thisManifest


    @classmethod
    def from_yamlFile( cls, yamlFilePath, rootDirectory ) :
        yamlData = loadYamlData( yamlFilePath )
        thisManifest = cls.from_yamlData( yamlData, rootDirectory )

        return thisManifest


def loadYamlData( yamlFilePath ) :
    with open( yamlFilePath, 'r' ) as yamlFile :
        yamlData = yaml.load( yamlFile )

    return yamlData
