# BOTLIB - Framework to program bots !!
#
# bot/cmnd/doc.py (docs)
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

""" documentation related commands. """

from bot import __version__, __txt__, _starttime
from bot.loader import Loader
from bot.utils.time import elapsed

import time

ldr = Loader()

def cmds(event):
    """ show list of commands. """
    mod = ldr.modules("bot")
    event.reply(",".join(sorted(mod)))

cmds.perm = "USER"

def man(event):
    """ show descriptions of the available commands. """
    ldr.walk("bot")
    res = []
    for cmnd in sorted(ldr._cmds):
        description =  ldr._descriptions.get(cmnd, "")
        if description:
            res.append("    %-25s# %s" % (cmnd, str(description).lower().strip()))
    event.reply("\n".join(res))

man.perm = "USER"

def mods(event):
    """ show available modules. """
    modnames = ldr.modules("bot")
    event.reply("\n    ".join(modnames))

mods.perm = "USER"

def modules(event):
    """ show available modules. """
    modnames = ldr.modules("bot")
    res = []
    for name in modnames:
        try:
            mod = ldr.direct(name)
        except ImportError:
            pass
        res.append("    %-25s# %s" % (name, str(mod.__doc__).lower().strip()))
    event.reply("\n".join(res))

mods.perm = "USER"

def uptime(event):
    """ show uptime. """
    event.reply("uptime is %s" % elapsed(time.time() - _starttime))

uptime.perm = "USER"

def version(event):
    """ show version. """
    from bot import name    
    event.reply("%s %s" % (name.strip(), __version__))

version.perm = "USER"
