#
# Copyright (c) 2016 BlueData Software, Inc.
#

from __future__ import print_function



def autogenAppend(outputLines, autogenDict, entryDict):
    """
    Handle any pattern replacements requested by the user.
    """
    if not autogenDict.has_key('append'):
        return

    
    #for containerDst, replaceDict in autogenDict['replace'].iteritems():
    appendDict = autogenDict['append']
    for key in appendDict:
        outputLines.append("APPEND_FILE %s %s \n" %(key, appendDict[key]))
        outputLines.append("\n")
    return
