# BOTLIB - Framework to program bots !!
#
# bot/cmds/users.py
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

from bot.loader import Loader
from bot.obj import allowchar
from bot.thr import Launcher
from bot.users import Users

ldr = Loader()
lhr = Launcher()
users = Users()

""" commands to manage users. """

def delperm(event):
    """ delete permissions of an user. """
    try:
        origin, perm = event._parsed.args
    except:
        event.reply("delperm <origin> <perm>")
        return
    origin = users._userhosts.get(origin, origin)
    result = users.delete(origin, perm)
    if not result:
        event.reply("can't find user %s" % origin)
        return
    event.ok(origin, perm)

delperm.perm = "OPER"

def meet(event):
    """ create an user record. """
    try:
        origin = event._parsed.rest
    except:
        event.reply("meet <nick> [<perm1> <perm2>]")
        return
    orig = origin.strip()
    if not allowchar(orig):
        event.reply("%s is not allowed as a username" % orig)
        return
    if orig:
        orig = users._userhosts.get(orig, orig)
        u = users.meet(orig)
        if u:
            event.reply("user %s created" % orig)
        else:
            event.reply("%s is already introduced." % orig)

meet.perm = "OPER"

def perm(event):
    """ add/change permissions of an user. """
    try:
        origin, perms = event._parsed.args
    except:
        event.reply("perm <origin> <perm>")
        return
    origin = users._userhosts.get(origin, origin)
    u = users.perm(origin, perms)
    if not u:
        event.reply("can't find a user matching %s" % origin)
        return
    event.ok(origin)

perm.perm = "OPER"

def permissions(event):
    """ show permissions granted to a user. """
    perms = []
    for name, funcs in ldr._handlers.items():
        if event._parsed.rest in name:
            perms.extend([str(x.perm) for x in funcs if "perm" in dir(x)])
    event.reply("permissions: %s" % ",".join(set(perms)))

permissions.perm = "USER"

def perms(event):
    """ show permission of user. """
    origin = users._userhosts.get(event.origin, event.origin)
    u = users.fetch(origin)
    if u:
        event.reply("permissions are %s" % ",".join(u.perms))

perms.perm = "USER"

def u(event):
    """ show user selected by userhost. """
    if not event._parsed.rest:
        event.reply("u <origin>")
        return
    origin = event._parsed.args[0]
    origin = users._userhosts.get(origin, origin)
    u = users.fetch(origin)
    if u:
        event.reply(u.pure())
    else:
        event.reply("no user %s found." % origin)

u.perm = "USER"

def w(event):
    """ show user data. """
    u = users.fetch(event.origin)
    if u:
        event.reply(u)
    else:
        event.reply("no matching user found.")

w.perm = "USER"

