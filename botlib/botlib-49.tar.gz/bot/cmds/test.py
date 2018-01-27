# BOTLIB - Framework to program bots !!
#
# bot/cmds/test.py (test)
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

""" test commands. """

from bot.event import Event
from bot.handler import Handler
from bot.loader import Loader
from bot.obj import allowedchars, name
from bot.raw import RAW
from bot.thr import Launcher
from bot.users import Users

import random
import time

ldr = Loader()
lhr = Launcher()

def randomname():
    s = ""
    for x in range(8):
        s += random.choice(allowedchars)
    return s

def exceptions(event):
    from bot.utils.trace  import exceptions
    for ex in exceptions:
        event.reply(ex)

def test(event):
    """ echo origin. """
    event.reply("hello %s" % event.origin)

test.perm = "USER"

def tests(event):
    events = []
    bot = RAW()
    bot.verbose = True
    bot.walk("bot.cmds")
    bot.start()
    for cmnd in bot._cmds:
        if cmnd in ["all", "tests", "tinder", "reboot", "stop"]:
            continue
        e = Event()
        e.id = bot.id
        e.origin = "test@shell"
        e.txt = cmnd + " " + randomname()
        e.txt = e.txt.strip()
        bot.put(e)
        events.append(e)
    for e in events:
        e.wait()
    bot.stop()
    event.reply("#%s commands run." %  len(bot._cmds))
    
tests.perm = "OPER"

def tinder(event):
    """ loop an command nr of times. """
    if not event._parsed.args:
        event.reply('tinder <nr> <cmd>')
        return
    try:
        nr = int(event._parsed.args[0])
    except (IndexError, ValueError):
        nr = 10
    try:
        name = event._parsed.args[1]
    except IndexError:
        name = "tests"
    ldr.walk("bot")
    funcs = ldr._handlers.get(name, None)
    if not funcs:
        event.reply("tinder <nr> <cmd>")
        return
    e = Event()
    e.origin = "test@shell"
    for x in range(nr):
        for func in funcs:
            time.sleep(0.001)
            lhr.launch(func, event)
