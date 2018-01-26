#
# Copyright (c) 2016 BlueData Software, Inc.
#

from __future__ import print_function
from .. import SubCommand
from ..constants import *
from ..inmem_store import ENTRY_DICT

class ServiceRemove(SubCommand):
    """

    """

    def __init__(self, config, inmemStore, cmdObj):
        SubCommand.__init__(self, config, inmemStore, cmdObj, 'remove')

    def getSubcmdDescripton(self):
        return 'Remove service(s) from the current catalog entry. '

    def populateParserArgs(self, subparser):
        subparser.add_argument('srvcid', metavar='SERVICE_ID', type=str,
                               nargs='*', default=DEFAULT_STR_ALL,
                               help='Remove only the specified SERVICE_ID(s).\
                                     Removes all  services if no SERVICE_ID is specified')


    def run(self, processedArgs):
        entrydict = self.inmemStore.getDict(ENTRY_DICT)
        if processedArgs.srvcid == DEFAULT_STR_ALL:
            entrydict["services"] = []
            if entrydict.has_key("config"):
                entrydict["config"]["node_services"] = []
                print("All service(s) successfully removed")
                return True

        if entrydict.has_key("services"):
            services = entrydict.get("services")
            NewServicesList = [ s for s in services if s['id'] not in processedArgs.srvcid]
            entrydict["services"] = NewServicesList
            print("Deleted services : ", str(processedArgs.srvcid))
        else:
            print("No services found")

        #remove traces of removed services from cluster config
        if entrydict.has_key("config"):
            for c in entrydict["config"]["node_services"]:
                c["service_ids"] = [ ns for ns in c["service_ids"] if ns not in processedArgs.srvcid ]
            print("Removed corresponding services from cluster config")

        return True

    def complete(self, text, argsList):
        return []
