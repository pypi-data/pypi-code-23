#
# Copyright (c) 2016 BlueData Software, Inc.
#

from __future__ import print_function
from .. import SubCommand
from ..utils.misc import downloadFile, calculateMD5SUM
from ..inmem_store import ENTRY_DICT

class ImageDownload(SubCommand):
    """

    """
    def __init__(self, config, inmemStore, cmdObj):
        SubCommand.__init__(self, config, inmemStore, cmdObj, 'download')

    def getSubcmdDescripton(self):
        return 'Download the image file from a HTTP url and add it to the '    \
               'catalog entry.'

    def populateParserArgs(self, subparser):
        subparser.add_argument('-u', '--url', metavar='IMAGE_URL', type=str,
                               required=True, dest='imageurl',
                               help='HTTP URL for downloading the image. The '
                               'file is downloaded to the staging directory.')
        subparser.add_argument('--md5sum', metavar='MD5SUM', type=str,
                               required=True,
                               help='MD5 checksum of the image: used to verify '
                               'the checksum immediatly after downloading.')
        subparser.add_argument('--os', metavar="OS", dest="os", required=True,
                               choices=['centos6', 'rhel6', 'centos7', 'rhel7',
                                        'ubuntu16'], action='store',
                               help="The OS distribution of the container image.")

    def run(self, pargs):
        localfile = downloadFile(pargs.imageurl, pargs.md5sum, self.config)
        if localfile == None:
            return False

        return self.workbench.onecmd("image file --filepath %s --md5sum %s --os %s" %
                                            (localfile, pargs.md5sum, pargs.os))

    def complete(self, text, argsList):
        return []
