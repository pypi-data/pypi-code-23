# BOTLIB - Framework to program bots !!
#
# bot/cmds/loader.py
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

""" loader related commands. """

from bot.loader import Loader
from bot.thr import Launcher

ldr = Loader()
lhr = Launcher()

import logging

def reload(event):
    """ reload a plugin. """
    if not event._parsed.rest:
        event.reply(",".join([x.split(".")[-1] for x in ldr.modules("bot.cmds")]))
        return
    for modname in ldr.modules("bot"):
        if event._parsed.rest not in modname:
            continue
        try:
            mod = ldr.reload(modname, False)
            if mod:
                event.ok(modname)
            else:
                event.reply("no %s module foudn to reload." % modname)
        except (AttributeError, KeyError) as ex:
            event.reply("%s %s" % (modname, str(ex)))

reload.perm = "OPER"

def start(event):
    """ start a plugin. """
    if not event._parsed.args:
        modnames = [x.split(".")[-1] for x in ldr.modules("bot")]
        res = [x.split(".")[-1] for x in modnames]
        event.reply("choose one of %s" % ",".join(sorted(res)))
        return
    n = event._parsed.args[0]
    if  n == "rss":
        from bot.rss import Fetcher
        rss = Fetcher()
        lhr.launch(rss.start)
        return
    elif n == "irc":
        from bot.irc import IRC
        irc = IRC()
        irc.connect(event.nick, event.server)
        irc.join(event.channel)
    elif n == "xmpp":
        from bot.xmpp import XMPP
        xmpp = XMPP()
        xmpp.start()
        xmpp.connect(event.user or "monitor@localhost")
        xmpp.join(event.nick or "monitor", event.room or "test@conference.localhost")
    elif n == "udp":
        from bot.cmds.udp import UDP
        udp = UDP()
        udp.start()
    logging.warn("started %s" % n)
    event.ok(n)

start._threaded = True
start.perm = "OPER"

def stop(event):
    """ stop a plugin. """
    if not event._parsed.rest:
        event.reply("stop what ?")
        return
    n  = event._parsed.args[0]
    if n:
        lhr.kill(n.upper())

stop._threaded = True
stop.perm = "OPER"
