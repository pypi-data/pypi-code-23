def resolve(relpath, contextpath='$'):
    path = None
    if isinstance(relpath, basestring):
        if relpath[0] == '$':
            path = relpath
        elif relpath[0] == '.':
            path = "%s%s" % (contextpath, relpath)
        elif relpath[0] == '[':
            path = "%s.%s" % (contextpath, relpath)
        else:
            path = "%s.%s" % (contextpath, relpath)
    else:
        path = "%s.[%s]" % (contextpath, relpath)
    return path
