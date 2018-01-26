#
# Copyright (c) 2016 BlueData Software, Inc.
#

from __future__ import print_function

def autogenPermission(outputLines, autogenDict, entryDict):
    """
    Set permissions for files or directories as requested by the user.
    """
    if not autogenDict.has_key('perms'):
        return

    outputLines.append("\n")
    for containerDst, permsDict in autogenDict['perms'].iteritems():
        rwx = permsDict['rwx']
        uid = permsDict['uid'] if permsDict.has_key('uid') else None
        gid = permsDict['gid'] if permsDict.has_key('gid') else None

        if rwx:
            outputLines.append("chmod -v %s %s\n" % (rwx, containerDst))

        if uid and (not gid):
            outputLines.append("chown -v %s %s\n" %(uid, containerDst))

        if uid and gid:
            outputLines.append("chown -v %s:%s %s\n" %(uid, gid, containerDst))

    return
