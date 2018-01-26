#
# Copyright (c) 2016 BlueData Software, Inc.
#

from __future__ import print_function
from .. import SubCommand
from ..constants import *
from ..utils.complete import completeFileBrowse
from ..inmem_store import ENTRY_DICT
from ..utils.misc import constructDistroId as constructDistroId

import os
import json

class CatalogLoad(SubCommand):
    """

    """
    def __init__(self, config, inmemStore, cmdObj):
        SubCommand.__init__(self, config, inmemStore, cmdObj, 'load')

    def getSubcmdDescripton(self):
        return 'Load an existing catalog entry.'

    def populateParserArgs(self, subparser):
        subparser.add_argument('-f', '--filepath', metavar='FILE_PATH', type=str,
                               required=True, dest='filepath',
                               help='File path to an existing catalog entry json.')

    def run(self, pargs):
        if not os.path.exists(pargs.filepath):
            print("ERROR: '%s' doesn't exist." % (pargs.filepath))
            return False

        jsonData= {}
        with open(pargs.filepath, 'r') as f:
            jsonData = json.loads(f.read())

        distroId = jsonData.pop('distro_id', None)
        newDistroId = constructDistroId(self.inmemStore, self.config, distroId)
        if newDistroId != None:
            jsonData['distro_id'] = newDistroId.lower()
        else:
            return False

        self.inmemStore.setDict(ENTRY_DICT, jsonData)
        return True

    def complete(self, text, argsList):
        return completeFileBrowse(text, argsList)
