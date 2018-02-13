#!/usr/bin/python
import getpass

PW_CACHE = {}

def get_pass(key):
    if key in PW_CACHE:
        pw = PW_CACHE[key]
    else:
        pw = getpass.getpass('%s password:' % (key))

    return pw