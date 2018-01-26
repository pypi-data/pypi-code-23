#
# Copyright (c) 2016 BlueData Software, Inc.
#

from __future__ import print_function

def autogenServiceRegistration(outputLines, autogenDict, entryDict):
    """
    Service registration.
    """
    if not autogenDict.has_key('services'):
        print("WARNING: No services are defined for the app.")
        return

    outputLines.append("\n")
    for srvcid, srvcDict in autogenDict['services'].iteritems():
        if srvcDict.has_key('sysv'):
            outputLines.append("REGISTER_START_SERVICE_SYSV %s %s\n" % (srvcid,
                                                                        srvcDict['sysv']))

        if srvcDict.has_key('sysctl'):
            outputLines.append("REGISTER_START_SERVICE_SYSCTL %s %s\n" % (srvcid,
                                                                          srvcDict['sysctl']))


    return
