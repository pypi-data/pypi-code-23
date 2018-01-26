#
# Copyright (c) 2016 BlueData Software, Inc.
#

from __future__ import print_function
from .. import SubCommand
from ..constants import *
from ..inmem_store import ENTRY_DICT

class ClusterConfigurationAssign(SubCommand):
    """

    """

    def __init__(self, config, inmemStore, cmdObj):
        SubCommand.__init__(self, config, inmemStore, cmdObj, 'assign')

    def getSubcmdDescripton(self):
        return 'Defines a cluster configuration which essentially links ' +\
               'various roles with the expected services. Multiple calls ' +\
               'of this command with a same CONFIG_ID are allowed to ' +\
               'associate different roles and service(s).'

    def populateParserArgs(self, subparser):
        subparser.add_argument('-c', '--configid', metavar='CONFIG_ID', type=str,
                               default=DEFAULT_STR_DEFAULT,
                               help='A catalog entry wide unique configuration id.')
        subparser.add_argument('-r', '--roleid', metavar='ROLE_ID', type=str,
                               action='store', dest='roleid', required=True,
                               help='A catalog entry wide unique role identifier.')
        subparser.add_argument('-s', '--srvcids', metavar='SERVICE_ID', type=str,
                               required=True, dest='srvcids', nargs='+',
                               help='Service(s) to be assigned to role when '
                               'this configutaion is enabled.')

    def run(self, pArgs):
        if pArgs.configid != DEFAULT_STR_DEFAULT:
            print("ERROR: Only the 'default' configuration id is supported.")
            return False

        entryDict = self.inmemStore.getDict(ENTRY_DICT)
        if not entryDict.has_key("config"):
            self.workbench.onecmd("clusterconfig new --configid %s" % pArgs.configid)

        defaultConfigValue = entryDict["config"]

        # NOTE: defaultConfigValue is a reference so any modifications to it
        #       are reflected in the inmem entry right away.
        if not defaultConfigValue.has_key('selected_roles'):
            defaultConfigValues['selected_roles'] = [pArgs.roleid]
        elif pArgs.roleid not in defaultConfigValue['selected_roles']:
            defaultConfigValue["selected_roles"].append(pArgs.roleid)

        nodeServices = defaultConfigValue["node_services"]
        for nsDict in nodeServices:
            if nsDict.has_key('role_id') and nsDict['role_id'] == pArgs.roleid:
                srvcs = nsDict['service_ids']

                for srvc in pArgs.srvcids:
                    if srvc not in srvcs:
                        srvcs.append(srvc)

                # matched role_id in this config space.
                return True

        # NOTE: 'role add' also assigns 'ssh' with the role which ends up here.
        defaultConfigValue["node_services"].append({
                                                    "role_id" : pArgs.roleid,
                                                    "service_ids" : pArgs.srvcids
                                                   })

        return True

    def complete(self, text, argsList):
        return []
