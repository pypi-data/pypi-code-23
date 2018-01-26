#
# Copyright (c) 2016 BlueData Software, Inc.
#

from __future__ import print_function
import os
from .. import SubCommand
from ..constants import *
from ..utils.config import SECTION_WB, KEY_IMAGEDIR, KEY_APPCONFIGDIR
from ..inmem_store import ENTRY_DICT, DELIVERABLE_DICT

class SourcesPackage(SubCommand):
    """

    """

    def __init__(self, config, inmemStore, cmdObj):
        SubCommand.__init__(self, config, inmemStore, cmdObj, 'package')

    def getSubcmdDescripton(self):
        return 'Package sources in the catalog bundle. The following file and ' +\
         'directories are automatically packaged if they exist: appconfig, ' +\
         'images, logo (if specified using logo commands), the instruction ' +\
         '(if being used), catalog entry json file.'

    def populateParserArgs(self, subparser):
        subparser.add_argument('--additional', metavar='DIRorFILE', type=str,
                               dest='additional', nargs='*',
                               help='Any additional files or directories to be '
                               'included as part of the sources. If you are not '
                               'using the default directory structure, you must '
                               'specify all the files and directories to be '
                               'packaged.')

    def run(self, pargs):
        pkgFiles = []

        delivDict = self.inmemStore.getDict(DELIVERABLE_DICT)

        imageDir = self.config.get(SECTION_WB, KEY_IMAGEDIR)
        if os.path.exists(imageDir):
            pkgFiles.append(imageDir)

        appconfigDir = self.config.get(SECTION_WB, KEY_APPCONFIGDIR)
        if os.path.exists(appconfigDir):
            pkgFiles.append(appconfigDir)

        try:
            pkgFiles.append(delivDict["logo"])
        except Exception:
            ## Logo is allowed to be empty.
            pass

        try:
            pkgFiles.append(delivDict['entry'])
        except Exception:
            print("ERROR: 'catalog save ... ' must be executed before packaging sources.")
            return False

        if self.workbench.batchfile != None:
            pkgFiles.append(os.path.abspath(self.workbench.batchfile))

        if pargs.additional != None:
            for a in pargs.additional:
                pkgFiles.append(os.path.abspath(a))

        delivDict['sources'] = pkgFiles
        return True

    def complete(self, text, argsList):
        return []
