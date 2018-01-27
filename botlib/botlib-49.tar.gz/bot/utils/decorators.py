# BOTLIB - Framework to program bots !!
#
# bot/utils/decorators.py
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

""" decorators module. """

from bot.obj import Object

def get_args(func, *args, **kwargs):

    def do_func(*args, **kwargs):
        o = Object(kwargs)
        o.args = args
        kwargs["args"] = o
        return func(*args, **kwargs)
        return o

def locked(func, *args, **kwargs):

    """ locked decorator, use to lock decorator function. """

    lock = _thread.allocate_lock()

    def lockedfunc(*args, **kwargs):
        """ lockded function to wrap a function in. """
        lock.acquire()
        res = None
        try:
            res = func(*args, **kwargs)
        finally:
            try:
                lock.release()
            except:
                pass
        return res
    return lockedfunc

