
import logging
log = logging.getLogger(__name__)

import os
from glob import glob
try:
    from glob import escape
except:                                                 # support Python < 3.4
    import re
    magic_check = re.compile('([*?[])')
    def escape(s):
        drive, pathname = os.path.splitdrive(s)
        pathname = magic_check.sub(r'[\1]', pathname)
        return drive + pathname

def rglob(dirname, pattern, dirs=False, sort=True):
    """recursive glob, gets all files that match the pattern within the directory tree"""
    fns = []
    if os.path.isdir(dirname):
        fns = glob(os.path.join(escape(dirname), pattern))
        dns = [fn for fn 
                in [os.path.join(dirname, fn)
                    for fn in os.listdir(dirname)] 
                if os.path.isdir(fn)]
        if dirs==True:
            fns += dns
        for d in dns:
            fns += rglob(d, pattern)
        if sort==True:
            fns.sort()
    else:
        log.warn("not a directory: %r" % dirname)
    return fns
