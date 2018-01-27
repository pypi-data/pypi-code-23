# BOTLIB - Framework to program bots !!
#
# bot/clock.py
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

""" clock related commands. """

from bot.clock import Timed, _begintime
from bot.utils.time import elapsed, now, parse_time, to_time

import time

def begin(event):
    """ begin stopwatch. """
    global _begintime
    t = to_time(now())
    _begintime = t
    event.reply("time is %s" % time.ctime(t))

begin.perm = "USER"

def end(event):
    """ stop stopwatch. """
    diff = time.time() - _begintime
    if diff:
        event.reply("time elapsed is %s" % elapsed(diff))

end.perm = "USER"

def timer(event):
    """ timer command to schedule a text to be printed on a given time. stopwatch to measure elapsed time. """
    if not event._parsed.rest:
        event.reply("timer <string with time> <txt>")
        return
    seconds = 0
    line = ""
    try:
        target = parse_time(event.txt)
    except ValueError:
        event.reply("can't detect time")
        return
    if not target or time.time() > target:
        event.reply("already passed given time.")
        return
    t = Timed()
    t.services = "clock"
    t.prefix = "timer"
    t.txt = event._parsed.rest
    t.time = target
    t.done = False
    t.save()
    event.ok(time.ctime(target))

timer.perm = "USER"
