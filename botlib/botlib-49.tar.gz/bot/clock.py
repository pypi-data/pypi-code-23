# BOTLIB - Framework to program bots !!
#
# bot/clk.py (clock)
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

""" timer, repeater. timed daemon. """

from bot.event import Event
from bot.thr import Launcher

from bot.obj import Config, Object, name

import os
import logging
import threading
import time

_begintime = time.time()

class Timed(Event):
    """ Future Timer Object. """
    pass

class Timers(Object):

    """ run timers on their scheduled time. """

    def __init__(self, *args, **kwargs):
        self._stopped = False
        self.timers = Object()
        self._name = "Timers"
        self.ready()

    def server(self):
        while not self._stopped:
            time.sleep(1.0)
            remove = []
            for t, event in self.timers.items():
                if time.time() > t:
                    event.direct(event.txt)
                    remove.append(t)
            for r in remove:
                del self.timers[r]
        
    def start(self):
        """ search database for timers still running. """
        from .dbz import Db
        db = Db()
        for e in db.sequence("timed", self.cfg.latest):
            if e.done: continue
            if "time" not in e: continue
            if time.time() < int(e.time):
                self.timers[e.time] = e
        lhr.launch(self.server)
        
    def stop(self):
        """ stop the timers logger. """
        self._stopped = True

class Timer(Object):

    """ call a function as x seconds of sleep. """

    def __init__(self, sleep, func, *args, **kwargs):
        super().__init__()
        self._func = func
        self._name = kwargs.get("name", name(self._func))
        self.sleep = sleep
        self.args = args
        self.kwargs = kwargs
        try:
            self._event = self.args[0]
        except:
            self._event = Event()
        self._time = Object()

    def start(self):
        """ start the timer. """
        timer = threading.Timer(self.sleep, self.run, self.args, self.kwargs)
        timer.setName(self._name)
        timer.sleep = self.sleep
        timer._event = self._event
        timer._time = self._time
        timer._time.start = time.time()
        timer._time.latest = time.time()
        timer._func = self._func
        timer.start()
        return timer

    def run(self):
        """ run the registered function. """
        self._time.latest = time.time()
        self._func(*self.args, **self.kwargs)

    def exit(self):
        """ cancel the timer. """
        self.cancel()

class Repeater(Timer):

    """ repeat an funcion every x seconds. """

    def run(self):
        self._func(*self.args, **self.kwargs)
        self.start()
