# Copyright (c) 2016 BlueData Software, Inc.
#

from __future__ import print_function
from .. import SubCommand
from ..constants import *
from ..inmem_store import ENTRY_DICT
from ..utils.misc import constructDistroId as constructDistroId

class CatalogModify(SubCommand):
    """

    """
    def __init__(self, config, inmemStore, cmdObj):
        SubCommand.__init__(self, config, inmemStore, cmdObj, 'modify')

    def getSubcmdDescripton(self):
        return 'Allows slected fields in the catalog entry to be updated.'

    def populateParserArgs(self, subparser):
        subparser.add_argument('--distroid', metavar='DISTRO_ID', type=str,
                               action='store',
                               help='A BlueData catalog wide unique distro id.')
        subparser.add_argument('--name', dest='name', metavar="NAME",
                               type=str, action='store',
                               help='Catalog name for the end user. Enclose in '
                                    'double quotes for names with spaces.')
        subparser.add_argument('--depends_on', metavar='DISTRO_ID',
                               dest='dependsOn', type=str, default=None,
                               help='Distro id of another catalog this entry '
                               'depends on. This option is used to indicate '
                               'that this is an add-on catalog entry.')
        subparser.add_argument('--desc', metavar="DESCRIPTIOIN", dest='desc',
                               type=str, action='store',
                               help='Catalog description for the end user. Use '
                                    'double quotes to enclose the description.')
        subparser.add_argument('-v', '--version', metavar='VERSION', dest='version',
                               type=str, action='store',
                               help='Catalog entry version of the form: MAJOR.MINOR')
        subparser.add_argument('-c', '--categories', metavar='CATEGORIES',
                               type=str, dest='categories', action='store',
                               nargs='+',
                               help='A space separated list of categories this '
                                    'entry will be available under during cluster '
                                    'creation. All categories necessary must be '
                                    'specified.')
        subparser.add_argument('--catalogapi', metavar='CATALOG_API_VERSION',
                               dest='catalogapi', type=str,
                               help='Catalog api version used by this entry.')

    def run(self, pargs):
        if pargs.distroid != None:
            newDistroId = constructDistroId(self.inmemStore, self.config,
                                            pargs.distroid)
            if newDistroId != None:
                self.inmemStore.addField(ENTRY_DICT, "distro_id", newDistroId.lower())
            else:
                return False

        if pargs.name != None or pargs.desc != None:
            entryDict = self.inmemStore.getDict(ENTRY_DICT)
            labelDict = entryDict['label']

            if pargs.name != None:
                labelDict['name'] = pargs.name

            if pargs.desc != None:
                labelDict['descriptions'] = pargs.desc

        if pargs.dependsOn != None:
            self.inmemStore.addField(ENTRY_DICT, "distro_dependency", pargs.dependsOn)

        if pargs.version != None:
            self.inmemStore.addField(ENTRY_DICT, "version", pargs.version)

        if pargs.catalogapi != None:
            self.inmemStore.addField(ENTRY_DICT, "catalog_api_version", pargs.catalogapi)

        if pargs.categories != None:
            self.inmemStore.addField(ENTRY_DICT, "categories", pargs.categories)

        return True

    def complete(self, text, argsList):
        return []
