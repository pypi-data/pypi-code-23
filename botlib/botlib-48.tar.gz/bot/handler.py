# BOTLIB - Framework to program bots !!
#
# hdl.py (handler)
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

""" event handler based on queue.Queue. """

from bot import Bot
from bot.loader import Loader
from bot.obj import Default, Object, name
from bot.utils.misc import stripped
from bot.utils.trace import get_exception
from bot.users import Users

import logging
import queue
import select
import time
import os

class ENOWORKER(Exception):
     """ No available worker could be found. """
     pass
     
class Handler(Loader):

    """
        An engine is a front-end class to check for input and if ready ask the inherited class to construct an event based on this input.
        The created event is pushed to the base class (Handler) thats takes care of further event handling.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._queue = queue.Queue()
        self.users = Users()

    def dispatch(self, event):
        event.dispatch()

    def put(self, event):
        """ put an event to work. """
        self._queue.put_nowait(event)

    def handler(self, *args, **kwargs):
        """ select loop defering the creation of events to the bot's class. """
        from bot.core import launcher
        while not self._stopped:
            event = self._queue.get()
            if not event:
                break
            thr = launcher.launch(self.dispatch, event)
            event._thrs.append(thr)
        logging.info("stop %s" % self.type)

    def start(self):
        """ start the queued bot.  """
        from bot.core import launcher
        self._stopped = False
        launcher.launch(self.handler)

    def stop(self):
        """ stop the queued bot. """
        self._stopped = True
        self._queue.put(None)
