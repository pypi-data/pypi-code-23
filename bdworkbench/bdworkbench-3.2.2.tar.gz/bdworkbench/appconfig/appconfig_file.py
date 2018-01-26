#
# Copyright (c) 2016 BlueData Software, Inc.
#

from __future__ import print_function
from .. import SubCommand
from ..constants import *
from ..utils.misc import calculateMD5SUM, checkConfigApiVersion
from ..inmem_store import ENTRY_DICT, DELIVERABLE_DICT

import os

class AppconfigFile(SubCommand):
    """

    """
    def __init__(self, config, inmemStore, cmdObj):
        SubCommand.__init__(self, config, inmemStore, cmdObj, 'file')

    def getSubcmdDescripton(self):
        return 'Add a local file path to an appconfig package for the catalog entry.'

    def populateParserArgs(self, subparser):
        subparser.add_argument('-f', '--filepath', metavar='FILEPATH', type=str,
                               dest='filepath', required=True,
                               help='File path to the appconfig package on the '
                                    'local filesystem.')
        subparser.add_argument('--md5sum', metavar='MD5SUM', type=str,
                               help='MD5 checksum of the appconfig package. If '
                                    'this is not specified, checksum for the '
                                    'file is calculated.')
        subparser.add_argument('--configapi', metavar='CONFIG_API_VERSION',
                               dest='configapi', type=int, default=None,
                               help='The config api version used by the appconfig package.')

    def run(self, pArgs):
        if not os.path.exists(pArgs.filepath):
            print("ERROR: '%s' does not exist." % pArgs.filepath)
            return False

        configApi = None
        if pArgs.configapi != None:
            # User's specification always overrides what's in the json file.
            configApi = int(pArgs.configapi)
        else:
            entryDict = self.inmemStore.getDict(ENTRY_DICT)
            if entryDict.has_key('setup_package'):
                appconfig = entryDict['setup_package']
                if appconfig.has_key('config_api_version'):
                    configApi = int(appconfig['config_api_version'])

        ## If the config API is still not set complain.
        if configApi == None:
            print("ERROR: config_api_version is not specified.")
            print("       Use --configapi or specify it in the catalog entry JSON.")
            return False

        checkConfigApiVersion(pArgs.configapi)

        filename = os.path.basename(pArgs.filepath)
        absFilename = os.path.abspath(pArgs.filepath)
        checksum = pArgs.md5sum if (pArgs.md5sum != None) else calculateMD5SUM(absFilename)

        # Cache the full local path. This may be useful if we later generate a
        # catalog bundle.
        self.inmemStore.addField(DELIVERABLE_DICT, "appconfig", absFilename)
        self.inmemStore.addField(DELIVERABLE_DICT, "appconfigSum", checksum)

        self.inmemStore.addField(ENTRY_DICT, "setup_package",
                                                {"source_file": filename,
                                                 "config_api_version" : configApi,
                                                 "checksum": checksum})

        return True

    def complete(self, text, argsList):
        if len(argsList) < 2:
            path = argsList[0]
            if not os.path.isfile(path):
                dirpath = '.' if (os.path.dirname(argsList[0]) == '') else     \
                                                    os.path.dirname(argsList[0])
                filename = os.path.basename(argsList[0])
                if os.path.isdir(dirpath):
                    ret = [x if not os.path.isdir(os.path.join(dirpath,x)) else x + '/' \
                            for x in os.listdir(dirpath) if x.startswith(filename)]
                    return ret

        return []
