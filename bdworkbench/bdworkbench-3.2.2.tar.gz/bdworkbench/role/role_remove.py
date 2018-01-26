#
# Copyright (c) 2016 BlueData Software, Inc.
#

from __future__ import print_function
from .. import SubCommand
from ..constants import *
from ..inmem_store import ENTRY_DICT

class RoleRemove(SubCommand):
    """

    """
    def __init__(self, config, inmemStore, cmdObj):
        SubCommand.__init__(self, config, inmemStore, cmdObj, 'remove')

    def getSubcmdDescripton(self):
        return 'Remove role(s) from the current catalog entry. '

    def populateParserArgs(self, subparser):
        subparser.add_argument('roleid', metavar='ROLE_ID', type=str,
                               nargs='*', default=DEFAULT_STR_ALL,
                               help='Remove only the specified ROLE_ID(s). \
                                     Removes all roles if no ROLE_ID is specified')

    def run(self, processedArgs):
        entrydict = self.inmemStore.getDict(ENTRY_DICT)
        if processedArgs.roleid == DEFAULT_STR_ALL:
            entrydict["node_roles"] =[]
            if entrydict.has_key("config"):
                entrydict["config"]["node_services"] = []
                entrydict["config"]["selected_roles"] = []
                print("All role(s) successfully removed")
                return True

        if entrydict.has_key("node_roles"):
            roles = entrydict.get("node_roles")
            NewRolesList = [ r for r in roles if r['id'] not in processedArgs.roleid ]
            entrydict["node_roles"] = NewRolesList
            print("Deleted Roles : ", str(processedArgs.roleid))

        #remove traces of removed roles from cluster config
        if entrydict.has_key("config"):
            node_services = entrydict["config"]["node_services"]
            entrydict["config"]["node_services"]  = \
                [ ns for ns in node_services if ns['role_id'] not in processedArgs.roleid ]

            selected_roles = entrydict["config"]["selected_roles"]
            entrydict["config"]["selected_roles"] = \
                [ r for r in selected_roles if r not in processedArgs.roleid ]

            print("Removed corresponding roles from cluster config")

        return True

    def complete(self, text, argsList):
        return []
