#
# Copyright (c) 2016 BlueData Software, Inc.
#

from __future__ import print_function
from .. import SubCommand
from ..constants import *
from ..inmem_store import ENTRY_DICT

class RoleAdd(SubCommand):
    """

    """
    def __init__(self, config, inmemStore, cmdObj):
        SubCommand.__init__(self, config, inmemStore, cmdObj, 'add')

    def getSubcmdDescripton(self):
        return 'Add a new role to the catalog entry.'

    def populateParserArgs(self, subparser):
        subparser.add_argument('roleid', metavar='ROLE_ID', type=str,
                               help='A catalog entry wide unique role id.')
        subparser.add_argument('cardinality', metavar='CARDINALITY', type=str,
                               default=DEFAULT_STR_ONE,
                               help='Cardinality for the role.')

    def run(self, pArgs):
        self.inmemStore.appendValue(ENTRY_DICT, "node_roles", {"id": pArgs.roleid,
                                                               "cardinality": pArgs.cardinality})

        return self.workbench.onecmd("clusterconfig assign --configid default --roleid " +
                                     "%s --srvcids ssh" % (pArgs.roleid))

    def complete(self, text, argsList):
        return []
