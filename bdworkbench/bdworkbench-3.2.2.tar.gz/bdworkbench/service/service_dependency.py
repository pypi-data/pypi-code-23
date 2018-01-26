#
# Copyright (c) 2016 BlueData Software, Inc.
#
from __future__ import print_function
from .. import SubCommand
from ..constants import *
from ..inmem_store import ENTRY_DICT

class ServiceDependency(SubCommand):
    """
    
    """
    def __init__(self, config, inmemStore, cmdObj):
        SubCommand.__init__(self, config, inmemStore, cmdObj, 'dependency')

    def getSubcmdDescripton(self):
        return 'Defines how various services depend on each other.'

    def populateParserArgs(self, subparser):
        subparser.add_argument('srvcid', metavar='SERVICE_ID', type=str,
                               nargs='*',
                               help='Service id(s) that depend on some other '
                                    'service(s).')
        subparser.add_argument('-d', '--depends_on', metavar='DEPENDS_ON',
                               type=str, action='store', required=True,
                               dest='depson',
                               help='Which service they depend on?')

    def run(self, pArgs):
        """
        """
        srvcList = self.inmemStore.getDict(ENTRY_DICT)['services']
        for r, e in [(x, y) for x in pArgs.srvcid for y in [pArgs.depson]]:
            for d in srvcList:
                if d['id'] == r:
                    if d.has_key('depends_on') and (e not in d['depends_on']):
                        d['depends_on'].append(e)
                    else:
                        d['depends_on'] = [e]
                    break;

        return True

    def complete(self, text, argsList):
        return []
