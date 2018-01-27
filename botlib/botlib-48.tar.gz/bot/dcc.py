# BOTLIB - Framework to program bots !!
#
# bot/dcc.py (direct client to client bot)
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
# 9-1-2018 As the creator of this file, I disclaim all rights on  this file. 
#
# Bart Thate
# Heerhugowaard
# The Netherlands

""" direct client to client bot. """

from bot import Bot
from bot.event import Event
from bot.select import Select

import io
import logging
import os
import socket
import sys

class DCC(Select, Bot):

    """ do communication over a file descriptor. """

    cc = ""

    def event(self):
        """ create a DCC event, """
        txt = self._sockfile.readline()
        if len(txt) == 0:
            return
        txt = txt.strip()
        logging.warn("< %s" % txt)
        e = Event()
        e.cc = self.cc
        e.id = self.id
        e.txt = txt
        e.origin = self.origin or "root@dcc"
        e.parse()
        self.prep(e)
        return e

    def say(self, channel, txt, type="normal"):
        """ return text to the DCC socket. """
        try:
            self._sockfile.write(txt)
            self._sockfile.write("\n")
            self._sockfile.flush()
        except:
            pass

    def start(self, *args, **kwargs):
        """ start the DCC bot. """
        from bot.core import fleet
        self._target = args[0]
        self._resume.fd = self._target.fileno()
        self._sockfile = self._target.makefile("rw")
        Select.start(self)
        Bot.start(self)
        self.register_fd(self._resume.fd)
        self.walk("bot")
        self.ready()

