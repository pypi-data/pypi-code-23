#
# Copyright (c) 2016 BlueData Software, Inc.
#

from __future__ import print_function



def autogenReplace(outputLines, autogenDict, entryDict):
    """
    Handle any pattern replacements requested by the user.
    """
    if not autogenDict.has_key('replace'):
        return

    #for containerDst, replaceDict in autogenDict['replace'].iteritems():
    for pathDict in autogenDict['replace']:
        #print("DEBUG:",containerDst,replaceDict)
        #replaceDict = autogenDict['replace'][containerDst]
        pattern = pathDict['substitute']['pattern']
        containerDst = pathDict['path']
        macro = pathDict['substitute']['macro']
        outputLines.append("REPLACE_PATTERN %s %s %s\n" %(pattern,
                                                          containerDst,
                                                          macro))
        outputLines.append("\n")
    return
