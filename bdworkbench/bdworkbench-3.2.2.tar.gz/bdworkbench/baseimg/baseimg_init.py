#
# Copyright (c) 2016 BlueData Software, Inc.
#

from __future__ import print_function
from .. import SubCommand
from ..utils.config import SECTION_WB, KEY_SDKBASE

import os, shutil

class BaseimgInit(SubCommand):
    """

    """
    def __init__(self, config, inmemStore, cmdObj):
        SubCommand.__init__(self, config, inmemStore, cmdObj, 'init')

    def getSubcmdDescripton(self):
        return 'When manually developing appconfig script, this copies a few ' +\
               'useful scripts that you can use as starter code.'

    def populateParserArgs(self, subparser):
        subparser.add_argument('--os', dest='baseimg', action='store', required=True,
                               choices=['centos6', 'rhel6', 'centos7', 'rhel7', 'ubuntu16'],
                               help='Copy all the files related to building docker '
                               'image that can be used as a base for apps on BlueData '
                               'EPIC. The files are copied to the current directory.')

    def run(self, pArgs):
        sdkbase = self.config.get(SECTION_WB, KEY_SDKBASE)
        baseImgDir = os.path.join(sdkbase, "baseimg")
        depsSrcDir = os.path.join(baseImgDir, "deps")

        osBaseimgSrc = ''
        if (pArgs.baseimg == 'centos6') or (pArgs.baseimg == 'rhel6'):
            osBaseimgSrc = os.path.join(baseImgDir, "centos6")
            depsRelativeDir = os.path.join("template", "deps")
        elif (pArgs.baseimg == 'centos7') or (pArgs.baseimg == 'rhel7'):
            osBaseimgSrc = os.path.join(baseImgDir, "centos7")
            # No deps required for CentOS/RHEL 7 base images.
            depsRelativeDir = None
        elif (pArgs.baseimg == 'ubuntu16'):
            osBaseimgSrc = os.path.join(baseImgDir, "ubuntu")
            depsRelativeDir = os.path.join("ubuntu16", "deps")
        else:
            print("ERROR: Unknown baseimg - %s" % (pArgs.baseimg))
            return False

        destDir = os.path.join(os.getcwd(), pArgs.baseimg)
        if depsRelativeDir:
            depsDestDir = os.path.join(destDir, depsRelativeDir)
        else:
            depsDestDir = None

        try:
            if os.path.exists(destDir):
                print("ERROR: Destination directory exists.")
                print("ERROR: Please remove '%s' before proceeding." % (destDir))
                return False
            else:
                shutil.copytree(osBaseimgSrc, destDir)

                if depsDestDir:
                    shutil.copytree(depsSrcDir, depsDestDir)
        except Exception as e:
            print("ERROR:", e)
            return False

        return True

    def complete(self, text, argsList):
        return []
