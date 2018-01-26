# BOTLIB - Framework to program bots !!
#
# bot/__init__.py (bot package)
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

""" bot module containing the basic bot classes. """

import os
import time

__version__ = "47"
__txt__ = "Framework to program bots"

_starttime = time.time()

name = "BOTLIB"

from bot.obj import Config, Object
from bot.utils.trace import get, get_exception

import importlib
import logging
import os
import queue
import select
import sys
import time
import types

class ENOTIMPLEMENTED(Exception):
    """ the method is not implemented in the inheriting class. """
    pass

class ECHAR(Exception):
    """ characters are not allowed. """
    pass

class Bot(Object):

    """ virtual bot class. """

    cc = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._nrconnect = 0
        self._nrreconnect = 2
        self._outqueue = queue.Queue()
        self._resume = Object()
        self._stopped = False
        self.channel = ""
        self.channels = []
        if self.channel and self.channel not in self.channels:
            self.channels.append(self.channel)
        self.id = repr(self)
 
    def announce(self, txt):
        """ print text on joined channels. """
        if self.silent:
            return
        if not self.channels:
            self.raw(txt)
        for channel in self.channels:
            self.say(channel, txt)

    def cmd(self, txt):
        """ execute a command based on txt.  """
        from bot.event import Event
        from bot.core import fleet, start
        start()
        fleet.register(self)
        name = txt.split()[0]
        logging.warn("cmd %s" % name)
        event = Event()
        event.verbose = True
        event.id = self.id
        event.origin = "root@shell"
        event.txt = txt
        event.parse()
        event.dispatch()
        return event

    def connect(self, user="", passwd=""):
        """ connect to server with user/passwd credentials. """
        return False

    def disconnect(self, e):
        """ disconnect from the server. """
        pass

    def disconnected(self):
        """ disconnected callback. """
        pass

    def event(self, origin="", txt=""):
        e = Event()
        e.id = self.id
        e.origin = origin or self.server
        e.txt = txt
        return e

    def join(self, channel, password=""):
        """ join a channel. """
        pass

    def joinall(self):
        """ join all channels. """
        for channel in self.channels:
            self.join(channel)

    def nick(self, nick):
        """ set bot's nick. """
        pass

    def once(self, txt):
        """ run one command. """
        try:
            self.cmd(txt)
        except:
            pass
        self.ready()
        return self

    def out(self, channel, line):
        """ output text on channel. """
        self.say(channel, line)

    def prompt(self, *args, **kwargs):
        """ echo prompt to sys.stdout. """
        pass

    def raw(self, txt):
        """ send txt to server. """
        if self.verbose:
            print(txt)
        
    def reconnect(self, event=None):
        """ run a connect loop until connected. """
        while not self._stopped:
            self._nrconnect += 1
            try:
                self.connect()
                break
            except:
                logging.error(get_exception())
                time.sleep(self._nrconnect * 5.0)
            if self._nrconnect > self._nrreconnect:
                 break
        logging.warn("connected to %s" % self.server)
                         
    def say(self, channel, txt, *args):
        """ say something on a channel. """
        if type(txt) in [list, tuple]:
            txt = ",".join(txt)
        self.raw(txt)

    def start(self):
        """ virtual start method """
        from bot.core import fleet
        fleet.register(self)

    def stop(self):
        from bot.core import fleet
        fleet.delete(self)
