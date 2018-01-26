#
# Copyright (c) 2016 BlueData Software, Inc.
#

from __future__ import print_function
from .. import SubCommand
from ..constants import *
from ..inmem_store import ENTRY_DICT
from ..utils.misc import downloadFile, calculateMD5SUM

class LogoDownload(SubCommand):
    """

    """
    def __init__(self, config, inmemStore, cmdObj):
        SubCommand.__init__(self, config, inmemStore, cmdObj, 'download')

    def getSubcmdDescripton(self):
        return 'Download the logo file from a HTTP url and add it to the '    \
               'catalog feed entry.'

    def populateParserArgs(self, subparser):
        subparser.add_argument('-l', '--url', metavar='LOGO_URL', type=str,
                               dest='logourl', action='store', required=True,
                               help='HTTP URL for downloading the logo. The '
                               'file is downloaded to the staging directory.')
        subparser.add_argument('--md5sum', metavar='MD5SUM', type=str,
                               dest='md5sum', action='store', required=False,
                               help='MD5 checksum of the logo: used to verify '
                               'the checksum immediatly after downloading.')

    def run(self, pargs):
        localfile = downloadFile(pargs.logourl, pargs.md5sum, self.config)
        if localfile == None:
            return False

        return self.workbench.onecmd("logo file --filepath %s --md5sum %s" %
                                                    (localfile, pargs.md5sum))

    def complete(self, text, argsList):
        return []
