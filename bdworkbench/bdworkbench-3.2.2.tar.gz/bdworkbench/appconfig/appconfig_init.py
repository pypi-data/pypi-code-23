#
# Copyright (c) 2016 BlueData Software, Inc.
#

from __future__ import print_function
from .. import SubCommand
from .appconfig_autogen import copyAppconfigStarter

import os

class AppconfigInitcode(SubCommand):
    """

    """
    def __init__(self, config, inmemStore, cmdObj):
        SubCommand.__init__(self, config, inmemStore, cmdObj, 'init')

    def getSubcmdDescripton(self):
        return 'When manually developing appconfig script, this copies a few ' +\
               'useful scripts that you can use as starter code.'

    def populateParserArgs(self, subparser):
        subparser.add_argument('-d', '--dir', metavar='DESTINATION_DIR', type=str,
                               dest='destdir', required=True,
                               help='A directory where the starter code is to '
                                    'be copied. This directory and all its parents '
                                    'will be created if they do not already exist.')

    def run(self, pArgs):
        if not os.path.exists(pArgs.destdir):
            os.makedirs(pArgs.destdir)

        if os.path.isdir(pArgs.destdir):
            copyAppconfigStarter(self.config, pArgs.destdir)
        else:
            print("ERROR: '%s' is not a directory" % (pArgs.destdir))

        return False

    def complete(self, text, argsList):
        return []
