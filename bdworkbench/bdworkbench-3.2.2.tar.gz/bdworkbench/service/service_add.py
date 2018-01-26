#
# Copyright (c) 2016 BlueData Software, Inc.
#
from __future__ import print_function
from .. import SubCommand
from ..constants import *
from ..inmem_store import ENTRY_DICT, SIMPLESETUP_DICT

class ServiceAdd(SubCommand):
    """

    """

    def __init__(self, config, inmemStore, cmdObj):
        SubCommand.__init__(self, config, inmemStore, cmdObj, 'add')

    def getSubcmdDescripton(self):
        return 'Add a new service to the catalog entry.'

    def populateParserArgs(self, subparser):
        srvc_group = subparser.add_argument_group(title='Service definition',
                        description='Define the service for E')

        srvc_group.add_argument('--srvcid', metavar='SERVICE_ID', type=str,
                                required=True, dest='srvcid',
                                help='A catalog entry wide unique service id.')
        srvc_group.add_argument('-n', '--name', dest='name', type=str,
                                action='store', required=True,
                                help='Service name to be displayed.')
        srvc_group.add_argument('--export_as', metavar='EXPORTED_NAME', dest='export', type=str,
                                action='store',
                                help='The name this service is exported as in the bluedata UI')
        srvc_group.add_argument('-s', '--scheme', dest='scheme', type=str,
                                action='store', default=None,
                                help='URI scheme for the service, if any.')
        srvc_group.add_argument('--port', dest='port', type=int, action='store',
                                default=None,
                                help='URI port number, if any.')
        srvc_group.add_argument('--path', dest='path', type=str, action='store',
                                default=None,
                                help='URI path for the service, if any.')
        srvc_group.add_argument('--display', dest='isdash', action='store_true',
                                default=DEFAULT_BOOL_FALSE,
                                help='Display the service to the end user on the '
                                     'cluster details page.')

        scripts_group = subparser.add_argument_group(title='Service control',
                        description='Start scripts for controlling services.')
        scripts_group.add_argument('--sysv', dest='sysv', action='store',
                                   default=None,
                                   help='SystemV service name for managing the '
                                        'service\'s lifcycle')
        scripts_group.add_argument('--sysctl', dest='sysctl', action='store',
                                   default=None,
                                   help='SystemD unit name for managing the '
                                         'service\'s lifecycle')

        role_group = subparser.add_argument_group(title='Role assignment',
                        description='Assigning services to specific roles.')
        scripts_group.add_argument('--onroles', dest='onroles', action='store',
                                   default=None, nargs='+',
                                   help='Node role the service should be '
                                        'assigned to for the default configuration.')

    def run(self, pArgs):
        if pArgs.sysv and pArgs.sysctl:
            print("ERROR: Only one of --sysv and --sysctl is expected.")
            return False

        existing = self._get_existing_srvc(pArgs.srvcid)
        if existing == None:
            valueDict = {}
            self._update_srvc_dict(valueDict, pArgs)
            self.inmemStore.appendValue(ENTRY_DICT, "services", valueDict)

            self._update_autogen_dict(pArgs)
            self._update_clusterconfig(pArgs)
        else:
            self._update_srvc_dict(existing, pArgs)

        return True

    def _update_autogen_dict(self, pArgs):
        if pArgs.sysv or pArgs.sysctl:
            autogen = self.inmemStore.getDict(SIMPLESETUP_DICT)["autogen"]

            if pArgs.sysv:
                autogen['services'][pArgs.srvcid] = { 'sysv': pArgs.sysv}
            elif pArgs.sysctl:
                autogen['services'][pArgs.srvcid] = { 'sysctl': pArgs.sysctl}

    def _update_clusterconfig(self, pArgs):
        if pArgs.onroles:
            for role in pArgs.onroles:
                self.workbench.onecmd("clusterconfig assign -c default -r %s -s %s" % (role, pArgs.srvcid))

    def _update_srvc_dict(self, valueDict, pArgs):
        """

        """
        valueDict['id'] = pArgs.srvcid
        valueDict['label'] = {"name": pArgs.name}
        valueDict['endpoint'] = { "is_dashboard" : pArgs.isdash }
        if pArgs.export != None:
            valueDict["exported_service"] = pArgs.export

        if pArgs.scheme != None:
            valueDict["endpoint"]["url_scheme"] = pArgs.scheme

        if pArgs.port != None:
            valueDict["endpoint"]["port"] = str(pArgs.port)

        if pArgs.path != None:
            valueDict["endpoint"]["path"] = pArgs.path

        self._update_autogen_dict(pArgs)
        self._update_clusterconfig(pArgs)

    def _get_existing_srvc(self, srvcId):
        """

        """
        entryDict = self.inmemStore.getDict(ENTRY_DICT)
        try:
            services = entryDict["services"]

            for srvc in services:
                if srvc['id'] == srvcId:
                    return srvc
        except Exception as e:
            pass

        return None


    def complete(self, text, argsList):
        return []
