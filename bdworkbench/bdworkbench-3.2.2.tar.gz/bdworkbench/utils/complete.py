#
# Copyright (c) 2016 BlueData Software, Inc.
#
from __future__ import print_function

import os

def completeFileBrowse(text, argsList):
    if len(argsList) < 2:
        path = argsList[0]
        if not os.path.isfile(path):
            dirpath = '.' if (os.path.dirname(argsList[0]) == '') else     \
                                                os.path.dirname(argsList[0])
            filename = os.path.basename(argsList[0])
            if os.path.isdir(dirpath):
                ret = [x if not os.path.isdir(os.path.join(dirpath,x)) else x + '/' \
                        for x in os.listdir(dirpath) if x.startswith(filename)]
                return ret

    return []
