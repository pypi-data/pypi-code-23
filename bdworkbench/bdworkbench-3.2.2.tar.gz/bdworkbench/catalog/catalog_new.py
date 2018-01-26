# Copyright (c) 2016 BlueData Software, Inc.
#

from __future__ import print_function
from .. import SubCommand
from ..constants import *
from ..inmem_store import ENTRY_DICT
from ..utils.misc import constructDistroId as constructDistroId

class CatalogNew(SubCommand):
    """

    """
    def __init__(self, config, inmemStore, cmdObj):
        SubCommand.__init__(self, config, inmemStore, cmdObj, 'new')

    def getSubcmdDescripton(self):
        return 'Starts a session for creating a new catalog entry. ' +\
               'Any previouly started sessions will be lost unless they ' +\
               'were saved.'

    def populateParserArgs(self, subparser):
        subparser.add_argument('--distroid', metavar='DISTRO_ID', type=str,
                               required=True, action='store',
                               help='A BlueData catalog wide unique distro id.')
        subparser.add_argument('--name', dest='name', metavar="NAME",
                               type=str, action='store', required=True,
                               help='Catalog name for the end user. Enclose in '
                                    'double quotes for names with spaces.')
        subparser.add_argument('--depends_on', metavar='DISTRO_ID',
                               dest='dependsOn', type=str, default=None,
                               help='Distro id of another catalog this entry '
                               'depends on. This option is used to indicate '
                               'that this is an add-on catalog entry.')
        subparser.add_argument('--desc', metavar="DESCRIPTIOIN", dest='desc',
                               type=str, action='store', required=True,
                               help='Catalog description for the end user. Use '
                                    'double quotes to enclose the description.')
        subparser.add_argument('-v', '--version', metavar='VERSION', dest='version',
                               type=str, action='store', default=DEFAULT_STR_VERSION,
                               help='Catalog entry version of the form: MAJOR.MINOR')
        subparser.add_argument('-c', '--categories', metavar='CATEGORIES',
                               type=str, dest='categories', action='store',
                               nargs='+', default=DEFAULT_CATEGORY_HADOOP,
                               help='A space separated list of categories this '
                                    'entry will be available under during cluster '
                                    'creation. Any existing categories may be '
                                    'used or new one may also be defined here.')
        subparser.add_argument('--catalogapi', metavar='CATALOG_API_VERSION',
                               dest='catalogapi', type=str, default=DEFAULT_CATALOG_API_VER,
                               help='Catalog api version used by this entry.')

    def run(self, processedArgs):
        use_distroId = constructDistroId(self.inmemStore, self.config,
                                         processedArgs.distroid)
        if use_distroId == None:
            return False

        distroId = use_distroId.lower()
        self.inmemStore.clear(ENTRY_DICT)
        self.inmemStore.addField(ENTRY_DICT, "distro_id", "%s" % (distroId))
        self.inmemStore.addField(ENTRY_DICT, "label", {"name": processedArgs.name,
                                                       "description": processedArgs.desc})
        self.inmemStore.addField(ENTRY_DICT, "version", processedArgs.version)
        self.inmemStore.addField(ENTRY_DICT, "catalog_api_version",
                                 processedArgs.catalogapi)
        self.inmemStore.addField(ENTRY_DICT, "categories",
                                 processedArgs.categories)
        self.inmemStore.addField(ENTRY_DICT, "setup_package",
                                    {"config_api_version": DEFAULT_CONFIG_API_VER})
        if processedArgs.dependsOn != None:
            self.inmemStore.addField(ENTRY_DICT, "distro_dependency",
                                     processedArgs.dependsOn)

        return True

    def complete(self, text, argsList):
        return []
