#
# Copyright (c) 2016 BlueData Software, Inc.
#

from __future__ import print_function

import os
from .. import SubCommand
from ..constants import *
from ..utils.misc import downloadFile, calculateMD5SUM
from ..utils.misc import checkConfigApiVersion
from ..inmem_store import ENTRY_DICT

class AppconfigDownload(SubCommand):
    """

    """
    def __init__(self, config, inmemStore, cmdObj):
        SubCommand.__init__(self, config, inmemStore, cmdObj, 'download')

    def getSubcmdDescripton(self):
        return 'Download the appconfig package from a HTTP url and add it to ' \
               'the catalog entry.'

    def populateParserArgs(self, subparser):
        subparser.add_argument('-u', '--url', metavar='SETUP_PACKAGE_URL', type=str,
                               required=True, dest='appconfigurl',
                               help='HTTP URL for downloading the appconfig '
                               'package. The file is downloaded to the staging '
                               'directory.')
        subparser.add_argument('--md5sum', metavar='MD5SUM', type=str,
                               dest='md5sum', required=True,
                               help='MD5 checksum of the appconfig package: '
                               'used to verify the checksum immediatly after '
                               'downloading.')
        subparser.add_argument('--configapi', metavar='CONFIG_API_VERSION',
                               dest='configapi', type=str, default=DEFAULT_CONFIG_API_VER,
                               help='The config api version used by the appconfig package.')

    def run(self, pargs):
        localfile = downloadFile(pargs.appconfigurl, pargs.md5sum, self.config)
        if localfile == None:
            return False

        checkConfigApiVersion(pArgs.configapi)

        return self.workbench.onecmd("appconfig file --filepath %s --md5sum %s --configapi %s" %
                                        (localfile, pargs.md5sum, pargs.configapi))

    def complete(self, text, argsList):
        return []
