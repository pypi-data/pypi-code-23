#
# Copyright (c) 2016 BlueData Software, Inc.
#
from __future__ import print_function
from .. import SubCommand
from ..inmem_store import DELIVERABLE_DICT

class BuilderOrg(SubCommand):
    """

    """

    def __init__(self, config, inmemStore, cmdObj):
        SubCommand.__init__(self, config, inmemStore, cmdObj, 'organization')

    def getSubcmdDescripton(self):
        return 'Set the organization name for this catalog entry. This name is ' +\
               'used to disabiguate the entry\'s distro id as well as the ' +\
               'name of the docker image imported.'


    def populateParserArgs(self, subparser):
        subparser.add_argument('-n', '--name', dest='orgname', action='store',
                               required=True, default=None,
                               help='Organization\'s name. This must be a single '
                               'word with no spaces. The input will be converted '
                               'to all lowercase if any mixed or upper case is used.')
        return

    def run(self, pargs):
        if ' ' in pargs.orgname:
            print("ERROR: No space is allowed in the organization's name.")
            return False

        self.inmemStore.addField(DELIVERABLE_DICT, "orgname", pargs.orgname.lower())
        return True

    def complete(self, text, argsList):
        return []
