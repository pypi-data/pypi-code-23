#
# Copyright (c) 2016 BlueData Software, Inc.
#

from __future__ import print_function
from .. import SubCommand
from ..constants import *
from ..inmem_store import ENTRY_DICT

class ClusterConfigurationNew(SubCommand):
    """

    """

    def __init__(self, config, inmemStore, cmdObj):
        SubCommand.__init__(self, config, inmemStore, cmdObj, 'new')

    def getSubcmdDescripton(self):
        return 'Create a new configuration that maps various services and ' +\
               'roles with each other.'

    def populateParserArgs(self, subparser):
        subparser.add_argument('-c', '--configid', metavar='CONFIG_ID', type=str,
                               default=DEFAULT_STR_DEFAULT,
                               help='A catalog entry wide unique configuration id.')

    def run(self, pArgs):
        if pArgs.configid != DEFAULT_STR_DEFAULT:
            print("ERROR: Only 'default' configuration id is supported.")
            return False

        valueDict = {
                        "selected_roles": [],
                        "node_services" : [],
                        "config_choices": [],
                        "config_meta"   : {}
                    }
        self.inmemStore.addField(ENTRY_DICT, "config", valueDict)
        return True

    def complete(self, text, argsList):
        return []
