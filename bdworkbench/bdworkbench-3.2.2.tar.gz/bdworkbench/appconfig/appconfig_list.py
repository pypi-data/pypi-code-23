#
# Copyright (c) 2016 BlueData Software, Inc.
#

from __future__ import print_function
from .. import SubCommand
from ..utils import printDict
from ..inmem_store import ENTRY_DICT

class AppconfigList(SubCommand):
    """

    """
    def __init__(self, config, inmemStore, cmdObj):
        SubCommand.__init__(self, config, inmemStore, cmdObj, 'list')

    def getSubcmdDescripton(self):
        return 'List the configured appconfig package.'

    def populateParserArgs(self, subparser):
        return

    def run(self, pArgs):
        entrydict = self.inmemStore.getDict(ENTRY_DICT)
        if entrydict.has_key("setup_package"):
            printDict(entrydict["setup_package"], header="Appconfig package:")
        else:
            print("No appconfig configuration found.")

        return True

    def complete(self, text, argsList):
        return []
