#
# Copyright (c) 2016 BlueData Software, Inc.
#
from __future__ import print_function

import os

def printKeyVal(key,val):
    print(key,':',str(val))

def printDict(data, header=None, footer=None, indent=4):
    """
    Print the 'data' based on it's instance type with appropriate indentation.
    """
    if header != None:
        print(header)

    if isinstance(data, dict):
        for key, value in data.iteritems():
            print(indent * ' ', key, ': ', end='')
            if isinstance(value, dict):
                printDict(value, indent=indent+4)
            else:
                print(value)
    elif isinstance(data, list):
        for e in data:
            print(e, end=' ')
    elif isinstance(data, str):
        print(data)

    if footer != None:
        print(footer)

def isDebug():
    """

    """
    return os.getenv("BDS_SDK_DEBUG", 'false') == 'true'
