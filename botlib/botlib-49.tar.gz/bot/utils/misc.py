# BOTLIB - Framework to program bots !!
#
# bot.utils.misc
#
# Copyright 2017,2018 B.H.J Thate
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice don't have to be included.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN 
# THE SOFTWARE.
#
# 9-1-2018 As the creator of this file, I disclaim all rights on this file. 
#
# Bart Thate
# Heerhugowaard
# The Netherlands

"""  bot utils package.  """

from bot import __version__
from bot.defines import ENDC, BOLD

import logging
import sys
import time
import os

def stripped(jid):
    """ strip trailing part of a JID, the part after the / """
    try:
        return str(jid).split("/")[0]
    except:
        return str(jid)

def make_version(name="", version=""):
    """ format a version string. """
    if version:
        txt = "%s %s" % (name, version)
    else:
        txt = name
    return "%s%-8s -=- %s%s" % (BOLD, txt, time.ctime(time.time()), ENDC)

def hello(name="", version=""):
    """ print welcome message. """
    print(make_version(name, version=version) + "\n")

def list_eggs(filter=""):
    """ list eggs on sys.path. """
    for f in sys.path:
        if filter and filter not in f:
            continue
        yield f

def show_eggs(filter="bot"):
    """ print what eggs are loaded. """
    for egg in list_eggs(filter):
        logging.warn(egg)

def high(target, file_name):
    """ get the newest of filenames ending in the highest .digit. """
    highest = 0
    for i in os.listdir(target):
        if file_name in i:
            try:
                seqnr = i.split('.')[-1]
            except IndexError:
                continue
            try:
                if int(seqnr) > highest:
                    highest = int(seqnr)
            except ValueError:
                pass
    return highest

def highest(target, filename):
    """ return the file with the highest filename ending (after the last . there is supposed to be a digit. """
    nr = high(target, filename)
    return "%s.%s" % (filename, nr+1)

def locatedir(path, match=""):
    """ locate subdirectory of path. """
    for root, dirs, files in os.walk(path):
        for d in dirs:
            if root == path:
                continue
            if match and match not in d:
                continue
            yield root

def copydir(orig, dest):
    """ copy directory from orig to destination. """
    for root, dirs, files in os.walk(orig):
        for d in dirs:
            if root == orig:
                continue
            nr = copydir(dir, os.path.join(dest, d))
            counter = 0
            for fn in files:
                shutil.copy(os.path.join(root, d, fn), os.path.join(dest, fn))
                yield fn
