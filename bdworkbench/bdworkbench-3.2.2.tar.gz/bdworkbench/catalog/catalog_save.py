#
# Copyright (c) 2016 BlueData Software, Inc.
#

from __future__ import print_function
from __future__ import with_statement

from .. import SubCommand
from ..constants import *
from ..inmem_store import ENTRY_DICT, DELIVERABLE_DICT
from ..utils.config import KEY_STAGEDIR, SECTION_WB

import os
import json
import traceback

class CatalogSave(SubCommand):
    """

    """
    def __init__(self, config, inmemStore, cmdObj):
        SubCommand.__init__(self, config, inmemStore, cmdObj, 'save')

    def getSubcmdDescripton(self):
        return 'Saves the current in-memory state of the catalog entry to a file.'

    def populateParserArgs(self, subparser):
        subparser.add_argument('-f', '--filepath', metavar='FILE_PATH', type=str,
                               dest='file', default=None,
                               help='File path to save the catalog entry json. '
                                    'If this is not specified, the json file '
                                    'is saved in the \'staging_dir\' defined '
                                    'in bench.conf')
        subparser.add_argument('--force', action='store_true',
                               dest='force', default=False,
                               help='Overwrite the catalog entry json file if '
                                    'it already exists.')

    def run(self, pargs):
        if (pargs.file is not None) and (not pargs.file.endswith('.json')):
            print("ERROR: Filepath must end in .json", )
            return False

        entryDict = self.inmemStore.getDict(ENTRY_DICT)
        delivDict = self.inmemStore.getDict(DELIVERABLE_DICT)
        if not entryDict.has_key('distro_id'):
            print("ERROR: 'catalog load|new <args>' must be executed before saving.")
            return False

        if delivDict.has_key('registryUrl'):
            entryDict['image'] = {}
            entryDict['image']['image_name'] = delivDict['imageName']
            entryDict['image']['registry_url'] = delivDict['registryUrl']
            entryDict['image']['registry_auth_enabled'] = delivDict['registryAuthEnabled']
            entryDict['image']['content_trust_enabled'] = delivDict['contentTrustEnabled']

        if pargs.file == None:
            stagingDir = self.config.get(SECTION_WB, KEY_STAGEDIR)
            filepath = os.path.join(stagingDir, entryDict['distro_id'] + '.json')
            force = True
        else:
            filepath = pargs.file
            force = pargs.force

        try:
            if (not os.path.exists(filepath)) or (force == True):
                dirname = os.path.dirname(filepath)
                if (dirname is not '') and (not os.path.exists(dirname)):
                    os.makedirs(dirname)

                jsonData = json.dumps(entryDict, indent=4)
                with open(filepath, 'w') as f:
                    f.write(jsonData)

                delivDict['entry'] = filepath
                return True
            else:
                print("ERROR: '%s' already exists. Use --force to overwrite." %
                                    (filepath))
                return False
        except Exception as e:
            print("Failed to save catalog entry at '%s':" % filepath, e)
            traceback.print_exc()
            return False

    def complete(self, text, argsList):
        return []
