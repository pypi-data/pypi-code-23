# BOTLIB - Framework to program bots !!
#
# bot/cmds/oper.py
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

from bot import _starttime, __version__, __txt__
from bot.obj import Object, name
from bot.utils.shell import reset
from bot.utils.time import elapsed

import os
import sys
import time
import _thread

psformat = "%-4s %-8s %-60s"

def announce(event):
    from bot.core import fleet
    for bot in fleet:
        bot.announce(event._parsed.rest)

announce.perm = "OPER"

def cfg(event):
    from bot.core import cfg
    event.reply(cfg)
    
cfg.perm = "OPER"

def fleet(event):
    from bot.core import fleet
    for bot in fleet:
        event.reply(bot.nice())

fleet.perm = "OPER"

def load(event):
    """ force a plugin reload. """
    if not event._parsed.rest:
        event.reply(",".join([x.split(".")[-1] for x in ldr.modules("bot")]))
        return
    for modname in ldr.modules("bot"):
        if event._parsed.rest not in modname:
            continue
        try:
            mod = ldr.reload(modname, True)
            event.reply("load %s" % modname)
        except (AttributeError, KeyError) as ex:
            event.reply("%s %s" % (modname, str(ex)))

load.perm = "OPER"

def ps(event):
    """ show running threads. """
    from bot.core import launcher
    up = elapsed(int(time.time() - _starttime))
    result = []
    for thr in sorted(launcher.running(), key=lambda x: name(x)):
        obj = Object(vars(thr))
        if "sleep" in obj:
            up = obj.sleep - int(time.time() - obj._time.latest)
        else:
            up = int(time.time() - _starttime)
        thrname = name(thr)[1:] + ")"
        result.append((up, thrname, obj))
    nr = 0
    for up, thrname, obj in sorted(result, key=lambda x: x[0]):
        nr += 1
        res = psformat % (nr, elapsed(up), thrname[:30])
        event.reply(res.rstrip())

ps.perm = "OPER"

def real_reboot():
    """ actual reboot. """
    reset()
    os.execl(sys.argv[0], *(sys.argv + ["-r",]))

real_reboot.perm = "OPER"

def reboot(event):
    """ reboot the ldr, allowing statefull reboot (keeping connections alive). """
    print(event)
    event.announce("rebooting")
    real_reboot()

reboot.perm = "OPER"

def exit(event):
    """ stop the program. """
    _thread.interrupt_main()

exit.perm = "UBER"

quit = exit

def pid(event):
    """ show pid of the bot. """
    event.reply("pid is %s" % str(os.getpid()))

pid.perm = "OPER"

