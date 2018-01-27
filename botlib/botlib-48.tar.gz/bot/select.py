# BOTLIB - Framework to program bots !!
#
# bot/select.py
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

""" select based loop. """

from bot.loader import Loader
from bot.obj import Object
from bot.utils.time import elapsed
from bot.utils.trace import get_exception
from bot.users import Users

import logging
import os
import select
import sys
import time

class ENOTIMPLEMENTED(Exception):
    """ method is not implemented. """
    pass

users = Users()

class Select(Loader):

    """
        An engine is a front-end class to check for input and if ready ask the inherited class to construct an event based on this input.
        The created event is pushed to the base class that takes care of further event handling.

    """

    _poll = select.epoll()
 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._connected = Object()
        self._fds = []
        self._resume = Object()
        self._stopped = False
        self._threaded = False

    def dispatch(self, event):
        event.dispatch()

    def event(self):
        """ virutal method to create an event, should be inherited. """
        raise ENOTIMPLEMENTED()

    def events(self):
        """ use poll to see if a bot is ready to receive input and if so, call the event() method to create an event from this input. """
        fdlist = self._poll.poll()
        for fd, event in fdlist:
            try:
                yield self.event()
            except (KeyboardInterrupt, EOFError):
                return 
            except Exception as ex:
                self.unregister_fd(fd)
                logging.error(get_exception())
         
    def register_fd(self, fd):
        """ register filedescriptors to check for input. """
        if "fileno" in dir(fd):
            fd = fd.fileno()
        if fd in self._fds:
            logging.warn("%s already registered." % fd)
            return
        self._poll.register(fd)
        self._fds.append(fd)
        logging.info("engine on %s" % ",".join(str(x) for x in self._fds))
        return fd

    def select(self, *args, **kwargs):
        """ select loop defering the creation of events to the bot's class. """
        from bot.core import launcher
        while not self._stopped:
            for event in self.events():
                if not event:
                    self._stopped = True
                    break
                if event.pure:
                    try:
                        self.dispatch(event)
                    except:
                        print(get_exception())
                else:
                    thr = launcher.launch(self.dispatch, event)
                    event._thrs.append(thr)
        self.stop()

    def start(self, *args, **kwargs):
        """ start the select() method in it's own thread. """
        from bot.core import launcher
        self._stopped = False
        self._resume.fd2 = self._poll.fileno()
        os.set_inheritable(self._resume.fd2, os.O_RDWR)
        launcher.launch(self.select)
         
    def stop(self):
        """ unregister all filedescriptors and close the polling object. """
        logging.error("stop %s" % ",".join([str(x) for x in self._fds]))
        for fd in self._fds:
            self.unregister_fd(fd)

    def unregister_fd(self, fd):
        """ remove a filedescriptor from the polling object. """
        if fd in self._fds:
            self._fds.remove(fd)
        try:
            self._poll.unregister(fd)
        except (PermissionError, FileNotFoundError):
            pass

