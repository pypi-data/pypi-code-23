#
# Copyright (c) 2016 BlueData Software, Inc.
#

from __future__ import print_function
import os



def autogenExecute(outputLines, autogenDict, entryDict):
    """
    Handle any pattern replacements requested by the user.
    """
    if not autogenDict.has_key('execute'):
        return

    for roles, script in autogenDict['execute']:
        scriptPath = script if os.path.isabs(script) else os.path.join("${CONFIG_BASE_DIR}", script)

        if roles != None:
            outputLines.append("if")
            for index, role in zip(range(0, len(roles)), roles):
                if index != 0:
                    outputLines.append(" ||\\\n")

                outputLines.append(" [[ \"${ROLE}\" == '%s' ]]" % role)

            outputLines.append("; then \n")
            outputLines.append("    ")

        outputLines.append("bash %s || exit 2\n" %(scriptPath))

        if roles != None:
            outputLines.append("fi\n")

    return
