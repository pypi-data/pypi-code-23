# BOTLIB - Framework to program bots !!
#
# bot/cli.py (command line interface bot)
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

""" command line interface bot. """

from bot import Bot, __version__
from bot.event import Event
from bot.obj import Config, slice
from bot.select import Select
from bot.utils.log import level
from bot.utils.shell import cdir, parse_cli, set_completer

from bot.core import fleet, loader, launcher, db, users

import bot.obj as obj

import logging
import sys
import os

class CLI(Bot, Select):

    """ Command Line Interface Bot. """

    cc = ""

    def __init__(self, *args, **kwargs):
        Bot.__init__(self, *args, **kwargs)
        Select.__init__(self)
        self._started = False
        self._threaded = True
        self.prompted = False
        
    def event(self):
        """ must return an Event and block for input function. """ 
        e = Event()
        e.id = self.id
        e.cc = self.cc
        e.origin = "root@shell"
        e.txt = input()
        self.prompted = False
        e.txt = e.txt.rstrip()
        return e

    def dispatch(self, event):
        event.dispatch()
        event.wait()
        self.prompt()
        
    def prompt(self, *args, **kwargs):
        """ echo prompt to sys.stdout. """
        if self.prompted:
            return
        self.prompted = True
        sys.stdout.write("> ")
        sys.stdout.flush()

    def raw(self, txt):
        """ output txt to sys.stdout """
        #txt = txt.strip()
        try:
            sys.stdout.write(txt)
        except TypeError:
            sys.stdout.write(str(txt))
        sys.stdout.write("\n")
        sys.stdout.flush()

    def start(self, cfg):
        if cfg.args:
            return self.cmd(" ".join(cfg.args))
        elif cfg.shell:
            Bot.start(self)
            Select.start(self)
            self.register_fd(sys.stdin)
            self.services(cfg)
            self.prompt()
            self.wait()
        self.ready()
