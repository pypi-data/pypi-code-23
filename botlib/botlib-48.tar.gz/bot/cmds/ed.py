# BOTLIB - Framework to program bots !!
#
# bot/cmds/ed.py
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

from bot.obj import name
from bot.thr import Launcher

import json

lhr = Launcher()

def ed(event):
    """ show running threads. """
    args = event._parsed.args
    if not args:
        event.reply("ed <name> <key> <value>")
        return
    n = args[0]
    obj = None
    for thr in sorted(lhr.running(), key=lambda x: name(x)):
        if n.upper() not in str(thr).upper():
            continue
        try:
            obj = thr._func.__self__
            id = obj.id
        except:
            continue 
        if not obj:
            continue
        if n.lower() in id.lower():
            break
    if len(args) == 1:
        print(obj)
        return 
    key = args[1]
    if key not in obj:
        event.reply("EKEY %s" % key)
        return
    if len(args) == 2:
        event.reply('%s="%s"' % (key, obj[key]))
        return
    val = ""
    if len(args) > 3:
        val = args[2:]
    if len(args) == 3:
        val = args[2]
    try:
        val = int(val)
    except:
        try:
            val = float(val)
        except:
            pass
    if type(val) == list:
        obj[key] = list(val)
    elif val in ["True", "true"]:
        obj[key] = True
    elif val in ["False", "false"]:
        obj[key] = False
    else:
        try:
            val = '"%s"' % val
            obj[key] = json.loads(val)
        except (SyntaxError, ValueError) as ex:
            event.reply("%s: %s" % (str(ex), val))
            return
    if key == "user" and "@" in obj[key]:
        obj["username"], obj["server"] = obj[key].split("@")
    obj.save()
    event.reply("ok %s=%s" % (key, val))

ed.perm = "OPER"
