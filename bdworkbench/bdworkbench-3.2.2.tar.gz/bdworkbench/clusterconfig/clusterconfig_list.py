#
# Copyright (c) 2016 BlueData Software, Inc.
#

from __future__ import print_function
from .. import SubCommand
from ..constants import *
from ..utils import printDict
from ..inmem_store import ENTRY_DICT

class ClusterConfigurationList(SubCommand):
    """

    """

    def __init__(self, config, inmemStore, cmdObj):
        SubCommand.__init__(self, config, inmemStore, cmdObj, 'list')

    def getSubcmdDescripton(self):
        return 'Lists details about the various cluster configurations for ' +\
               'the current catalog entry. When one or more CONFIG_ID(s) are ' +\
               'specified, only details for those configurations will be displayed.'

    def populateParserArgs(self, subparser):
        subparser.add_argument('configid', metavar='CONFIG_ID', type=str,
                               nargs='*', default=DEFAULT_STR_ALL,
                               help='One or more space separated config id to '
                               'show the details of. If no config ids are '
                               'sepcified, details of all currently configured '
                               'config ids are shown.')

    def run(self, processedArgs):
        entrydict = self.inmemStore.getDict(ENTRY_DICT)
        if entrydict.has_key("config"):
            printDict(entrydict.get("config"), header="Cluster Configuration:",
                      footer="")
            print("")
        else:
            print("No cluster config available.")

        return True

    def complete(self, text, argsList):
        return []
