#
# Copyright (c) 2016 BlueData Software, Inc.
#

from __future__ import print_function
from .. import SubCommand
from ..utils.misc import calculateMD5SUM
from ..inmem_store import ENTRY_DICT, DELIVERABLE_DICT

import os

class LogoFile(SubCommand):
    """

    """
    def __init__(self, config, inmemStore, cmdObj):
        SubCommand.__init__(self, config, inmemStore, cmdObj, 'file')

    def getSubcmdDescripton(self):
        return 'Add a local file path to a logo for the catalog entry.'

    def populateParserArgs(self, subparser):
        subparser.add_argument('-f', '--filepath', metavar='FILEPATH', type=str,
                               required=True, dest='filepath',
                               help='File path to the appconfig package on the '
                                    'local filesystem.')
        subparser.add_argument('-m', '--md5sum', metavar='MD5SUM', type=str,
                               action='store', dest='md5sum', required=False,
                               help='MD5 checksum of the appconfig package. If '
                                    'this is not specified, checksum for the '
                                    'file is calculated.')

    def run(self, pArgs):
        if not os.path.exists(pArgs.filepath):
            print("ERROR: '%s' does not exist." % pArgs.filepath)
            return False

        filename = os.path.basename(pArgs.filepath)
        absFilename = os.path.abspath(pArgs.filepath)
        checksum = pArgs.md5sum if (pArgs.md5sum != None) else calculateMD5SUM(absFilename)

        # Cache the full local path. This may be useful if we later generate a
        # catalog bundle.
        self.inmemStore.addField(DELIVERABLE_DICT, "logo", absFilename)
        self.inmemStore.addField(DELIVERABLE_DICT, "logoSum", checksum)

        # Update the entry dict for the json.
        self.inmemStore.addField(ENTRY_DICT, "logo",
                                        {"source_file": filename,
                                         "checksum": checksum})
        return True

    def complete(self, text, argsList):
        if len(argsList) < 2:
            path = argsList[0]
            if not os.path.isfile(path):
                dirpath = '.' if (os.path.dirname(argsList[0]) == '') else     \
                                                    os.path.dirname(argsList[0])
                filename = os.path.basename(argsList[0])
                if os.path.isdir(dirpath):
                    ret = [x if not os.path.isdir(os.path.join(dirpath,x)) else x + '/' \
                            for x in os.listdir(dirpath) if x.startswith(filename)]
                    return ret

        return []
