# BOTLIB - Framework to program bots !!
#
# log.py (logging)
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

""" log module to set standard format of logging. """

from bot.obj import Object

import logging.handlers
import logging
import socket
import os

def cdir(path):
    """ create directory. """
    res = ""
    for p in path.split(os.sep):
        res += "%s%s" % (p, os.sep)
        padje = os.path.abspath(os.path.normpath(res))
        try:
            os.mkdir(padje)
        except (IsADirectoryError, NotADirectoryError, FileExistsError):
            pass
    return True

homedir = os.path.expanduser("~")
curdir = os.getcwd()
logdir = homedir + os.sep + ".logs"
cdir(logdir)

try:
    hostname = socket.getfqdn()
except:
    hostname = "localhost"

datefmt = '%H:%M:%S'

format = Object()
format.large = "%(asctime)-8s %(module)10s.%(lineno)-4s %(message)-50s (%(threadName)s)"
format.source = "%(asctime)-8s %(message)-50s (%(module)s.%(lineno)s)"
format.time = "%(asctime)-8s %(message)-72s"
format.log = "%(message)s"
format.super = "%(asctime)-8s -=- %(message)-50s -=- (%(module)s.%(lineno)s)" 
format.normal = "%(asctime)-8s -=- %(message)-60s"
format.plain = "%(message)-0s"

class DumpHandler(logging.StreamHandler):

    """ Logger that logs nothing. """

    def emit(self, record):
        pass

class Formatter(logging.Formatter):

    """ Formatter that strips coloring (even more yes!) from the Logger. """

    def format(self, record):
        target = str(record.msg)
        if not target:
            target = " "
        if target[:2] in ["> ", "< ", "! ", "# ", "^ ", "- ", "& "]:
            target = target[2:]
        record.msg = target
        return logging.Formatter.format(self, record)

def level(level, form="plain"):
    """ set loglevel to provided level. """ 
    level = level.upper()
    logger = logging.getLogger("")
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)
    dhandler = DumpHandler()
    logger.setLevel(level)
    logger.addHandler(dhandler)
    #fmt = format_log
    fmt = format.get(form, "normal")
    formatter = Formatter(fmt, datefmt=datefmt)
    ch = logging.StreamHandler()
    ch.propagate = False
    ch.setFormatter(formatter)
    ch.setLevel(level)
    logger.addHandler(ch)
    formatter_clean = Formatter(format, datefmt=datefmt)
    filehandler = logging.handlers.TimedRotatingFileHandler(os.path.join(logdir, "bot.log"), 'midnight')
    filehandler.setLevel(level)
    logger.addHandler(filehandler)
    return logger
    
def log_cb(event):
    event.save()
    
log_cb.cbs = ["PRIVMSG", "JOIN", "PART", "QUIT", "CLI"]

def log(level, error):
    """ log a line on given level. """
    l = LEVELS.get(str(level).lower())
    logging.log(l, error)
