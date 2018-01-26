#
# Copyright (c) 2016 BlueData Software, Inc.
#

from __future__ import print_function
from .. import SubCommand
from ..constants import *
from ..utils import printKeyVal
from ..inmem_store import ENTRY_DICT

class RoleList(SubCommand):
    """

    """
    def __init__(self, config, inmemStore, cmdObj):
        SubCommand.__init__(self, config, inmemStore, cmdObj, 'list')

    def getSubcmdDescripton(self):
        return 'List details of role(s) defined in the catalog entry.'

    def populateParserArgs(self, subparser):
        subparser.add_argument('roleid', metavar='ROLE_ID', type=str,
                               nargs='*', default=DEFAULT_STR_ALL,
                               help='Show details of the specified ROLE_ID(s) only.')

    def run(self, processedArgs):
        entrydict = self.inmemStore.getDict(ENTRY_DICT)
        if entrydict.has_key("node_roles"):
            roles=entrydict.get("node_roles")
            for role in roles:
                print("")
                for k,v in role.items():
                    printKeyVal(k,v)
            print("")
        else:
            print("No role configured.")

        return True

    def complete(self, text, argsList):
        return []
