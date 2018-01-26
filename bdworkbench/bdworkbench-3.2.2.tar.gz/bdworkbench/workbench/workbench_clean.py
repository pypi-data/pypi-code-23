#
# Copyright (c) 2016 BlueData Software, Inc.
#
from __future__ import print_function
from .. import SubCommand
from ..constants import *
from ..utils.config import KEY_BASE, KEY_LOGDIR, KEY_IMAGEDIR, KEY_STAGEDIR
from ..utils.config import KEY_APPCONFIGDIR, SECTION_WB
import os, shutil

class WorkbenchClean(SubCommand):
    """

    """

    def __init__(self, config, inmemStore, cmdObj):
        SubCommand.__init__(self, config, inmemStore, cmdObj, 'clean')

    def getSubcmdDescripton(self):
        return 'Cleanup all temporary artifacts any log files that may have ' +\
             'been generated during the package process.'

    def populateParserArgs(self, subparser):
        return

    def run(self, pargs):
        logDir = self.config.get(SECTION_WB, KEY_LOGDIR)
        stageDir = self.config.get(SECTION_WB, KEY_STAGEDIR)

        if os.path.exists(logDir):
            shutil.rmtree(logDir)

        if os.path.exists(stageDir):
            shutil.rmtree(stageDir)

        return True

    def complete(self, text, argsList):
        return []
