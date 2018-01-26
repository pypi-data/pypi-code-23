#
# Copyright (c) 2016 BlueData Software, Inc.
#
from __future__ import print_function
from .. import SubCommand
from ..constants import *
from ..utils.config import KEY_BASE, KEY_LOGDIR, KEY_IMAGEDIR, KEY_STAGEDIR
from ..utils.config import KEY_APPCONFIGDIR, SECTION_WB
import os, shutil

class WorkbenchInitapp(SubCommand):
    """

    """

    def __init__(self, config, inmemStore, cmdObj):
        SubCommand.__init__(self, config, inmemStore, cmdObj, 'initapp')

    def getSubcmdDescripton(self):
        return 'Initialize a workspace for catalog entry development.'

    def populateParserArgs(self, subparser):
        subparser.add_argument('-d', '--basedir', dest='basedir', action='store',
                               default=os.getcwd(),
                               help='Initialize the workbench files at the '
                               'specified directory.')
        subparser.add_argument('-f', '--force', dest='force',
                               action='store_true', default=False,
                               help='Force workbench initialization.')
        return

    def run(self, pargs):
        base = self.config.get(SECTION_WB, KEY_BASE)

        if not pargs.force:
            if len(os.listdir(base)) > 0:
                print("ERROR: The current working directory already contains some files.")
                print("       It is advised to initialize the workspace in an empty dir.")
                print("       This behaviour may be overridden by using -f/--force.")

                return False

        # Initialize the workspace:
        #   - Create logs directory
        #   - Create image directory
        #   - Create components directory
        #   - Initialize appconfig directory with starter code.
        # logDir = self.config.get(SECTION_WB, KEY_LOGDIR)
        imageDir = self.config.get(SECTION_WB, KEY_IMAGEDIR)
        # stageDir = self.config.get(SECTION_WB, KEY_STAGEDIR)
        appconfigDir = self.config.get(SECTION_WB, KEY_APPCONFIGDIR)

        try:
            if not os.path.exists(base):
                os.mkdirs(base)

            # os.mkdir(logDir)
            os.mkdir(imageDir)
            # os.mkdir(stageDir)

            ## NOTE: self.workbench is a BDwb object.
            self.workbench.onecmd("appconfig init --dir %s" % (appconfigDir))

            return True
        except Exception as e:
            print("ERROR: Failed to initialize workbench", "-", e)

            self.workbench.onecmd("workbench clean")
            return False

    def complete(self, text, argsList):
        return []
