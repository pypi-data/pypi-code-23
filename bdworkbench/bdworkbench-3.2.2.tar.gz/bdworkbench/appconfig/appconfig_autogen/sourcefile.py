#
# Copyright (c) 2017 BlueData Software, Inc.
#

from __future__ import print_function
import os



def autogenSourceFile(outputLines, autogenDict):
    """
    Add an line that sources the give file.
    """
    if not autogenDict.has_key('sourcefiles'):
        return

    for roles, script in autogenDict['sourcefiles']:
        scriptPath = script if os.path.isabs(script) else os.path.join("${CONFIG_BASE_DIR}", script)

        if roles != None:
            outputLines.append("if")
            for index, role in zip(range(0, len(roles)), roles):
                if index != 0:
                    outputLines.append(" ||\\\n")

                outputLines.append(" [[ \"${ROLE}\" == '%s' ]]" % role)

            outputLines.append("; then\n")
            outputLines.append("    ")

        outputLines.append("source %s || exit 1\n" %(scriptPath))

        if roles != None:
            outputLines.append("fi")

    return
