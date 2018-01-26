#
# Copyright (c) 2016 BlueData Software, Inc.
#

from __future__ import print_function
from .. import SubCommand
from ..constants import *
from ..utils import printKeyVal
from ..inmem_store import ENTRY_DICT

class ServiceList(SubCommand):
    """

    """

    def __init__(self, config, inmemStore, cmdObj):
        SubCommand.__init__(self, config, inmemStore, cmdObj, 'list')

    def getSubcmdDescripton(self):
        return 'List service(s) for the current catalog entry.'

    def populateParserArgs(self, subparser):
        subparser.add_argument('srvcid', metavar='SERVICE_ID', type=str,
                               nargs='*', default=DEFAULT_STR_ALL,
                               help='Show details for the specified SERVICE_ID(s).')

    def run(self, processedArgs):
        entrydict = self.inmemStore.getDict(ENTRY_DICT)
        if entrydict.has_key("services"):
            services=entrydict.get("services")
            for service in services:
                print("")
                for k,v in service.items():
                    printKeyVal(k,v)
            print("")
        else:
            print("No service configured.")

        return True

    def complete(self, text, argsList):
        return []
