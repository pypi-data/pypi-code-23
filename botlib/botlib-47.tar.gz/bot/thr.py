# BOTLIB - Framework to program bots !!
#
# thr.py (thread)
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

""" threading module. """

from bot.obj import fromstring, name

import logging
import queue
import string
import time
import threading

class ENAME(Exception):
    """ name is not allowed. """
    pass

class Task(threading.Thread):

    """ Task are adapted Threads. """

    def __init__(self, *args, **kwargs):
        super().__init__(None, self.run, "", [], {}, daemon=False)
        self._queue = queue.Queue()
        self._ready = threading.Event()
        self._result = []

    def __iter__(self):
        """ return self as an iterator. """
        return self

    def __next__(self):
        """ yield next value. """
        for k in dir(self):
            yield k

    def put(self, *args, **kwargs):
        """ send an event to the task. """
        self._queue.put_nowait((args[0], args[1:], kwargs))

    def run(self):
        """ take an event from the queue and proces it. """
        (func, args, kwargs) = self._queue.get()
        self._func = func
        self._begintime = time.time()
        self._starttime = time.time()
        try:
            n = args[0].txt.split()[0]
        except (IndexError, AttributeError) as ex:
            n = name(func)
        self.setName(n)
        self._result = func(*args, **kwargs)
        self.ready()
        return self._result

    def isSet(self):
        """ see if the object ready flag is set. """
        return self._ready.isSet()

    def join(self, sleep=None):
        """ join this task and return the result. """
        #self.wait()
        super().join(sleep)
        return self._result

    def ready(self):
        """ signal the event as being ready. """
        self._ready.set()

    def clear(self):
        """ clear the ready flag. """
        self._ready.clear()

    def wait(self, sec=180.0):
        """ wait for the task to be ready. """
        self._ready.wait(sec)
        return self._result

class Launcher(object):

    """ Laucher is able to launch a Task (see task.py). """

    cc = "!"

    def waiter(self, thrs, timeout=None):
        """ wait for tasks to finish. """
        result = []
        for thr in thrs:
            if not thr:
                continue
            try:
                res = thr.join(timeout)
                result.append(res)
            except AttributeError:
                pass
            except KeyboardInterrupt:
                break
        return result

    def launch(self, *args, **kwargs):
        """ launc a function with argument in it's own thread. """
        logging.debug("launch %s" % str(args[0]))
        t = Task(**kwargs)
        t.start()
        t.put(*args, **kwargs)
        return t

    def kill(self, thrname=""):
        """ kill tasks matching the provided name. """
        thrs = []
        for thr in self.running(thrname):
            if thrname and thrname not in str(thr):
                continue
            if "cancel" in dir(thr):
                thr.cancel()
            elif "exit" in dir(thr):
                thr.exit()
            elif "stop" in dir(thr):
                thr.stop()
            else:
                continue
            thrs.append(thr)
        return thrs

    def running(self, tname=""):
        """ show what tasks are running. """
        for thr in threading.enumerate():
            if str(thr).startswith("<_"):
                continue
            yield thr
