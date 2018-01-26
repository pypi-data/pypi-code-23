# BOTLIB - Framework to program bots !!
#
# cmds/db.py
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

""" database related commands. """

from bot.db import Db
from bot.utils.time import day, to_day

import os
import time

db = Db()

def attr(event):
    """ show attributes of an object type. """
    from bot.obj import cfg
    if not event._parsed.args:
         options = ",".join(os.listdir(cfg.workdir))
         event.reply("attr <prefix>, use one of %s" % options)
         return
    prefix = event._parsed.args[0]
    try:
        keys = event._parsed.args[1:]
    except:
        keys = []
    obj = db.last(prefix)
    if obj:
        for key in keys:
            obj = getattr(obj, key, None)
        try:
            res = obj.keys()
        except AttributeError:
            res = []
            for o in obj:
                res.extend(o.keys())
            res = set(res)
        event.reply("\n".join(sorted([x for x in res if not x.startswith("_")])))
    else:
        event.reply("no %s prefix found." % event._parsed.args[0])

attr.perm = "USER"

def deleted(event):
    """ show deleted records. """
    event.nodel = True
    nr = 0
    for obj in db.selected(event):
        if "deleted" in dir(obj) and obj.deleted:
            nr += 1
            event.display(obj, str(nr))

deleted.perm = "USER"

def find(event):
    """ present a list of objects based on prompt input. """
    nr = 0
    seen = []
    for obj in db.selected(event):
        for key in event._parsed.uniqs.keys():
            val =  getattr(obj, key, None)
            if val and val in seen:
                continue
            else:
                seen.append(val)
        if "d" in event._parsed.enabled:
            event.reply(obj)
        else:
            event.display(obj, str(nr))
        nr += 1

find.perm = "USER"

def first(event):
    """ show the first record matching the given criteria. """
    obj = db.first(*event._parsed.args)
    if obj:
        event.reply(obj)

first.perm = "USER"

def fix(event):
    """ fix a object by loading and saving it. """
    fn = event._parsed.rest
    fn = os.path.abspath(fn)
    if not fn:
        event.reply("fix <path>")
        return
    if not os.path.isfile(fn):
        event.reply("%s is not a file" % fn)
        return
    o = Object()
    o.load(fn)
    p = o.save()
    event.reply("saved %s" % p)

fix.perm = "OPER"

def last(event):
    """ show last objectect matching the criteria. """
    if not event._parsed.args:
        event.reply("last <prefix> <value>")
        return
    obj = db.last(*event._parsed.args)
    if obj:
        event.reply(obj)

last.perm = "USER"

def ls(event):
    """ show subdirs in working directory. """
    from bot.obj import cfg
    event.reply(" ".join(os.listdir(cfg.workdir)))

ls.perm = "USER"

def restore(event):
    """ set deleted=False in selected records. """
    nr = 0
    event.nodel = True
    for obj in db.selected(event):
        obj.deleted = False
        obj.sync()
        nr += 1
    event.ok(nr)

restore.perm = "OPER"

def rm(event):
    """ set deleted flag on objects. """
    nr = 0
    for obj in db.selected(event):
        obj.deleted = True
        obj.sync()
        nr += 1
    event.ok(nr)

rm.perm = "OPER"

def today(event):
    """ show last week's logged objects. """
    event._parsed.start = to_day(day())
    event._parsed.end = time.time()
    nr = 0
    for obj in db.selected(event):
        nr += 1
        event.display(obj, str(nr))

today.perm = "USER"

def week(event):
    """ show last week's logged objects. """
    event._parsed.start = to_day(day()) - 7 * 24 * 60 * 60
    event._parsed.end = time.time()
    nr = 0
    for obj in db.selected(event):
        nr += 1
        event.display(obj, str(nr))

week.perm = "USER"

def yesterday(event):
    """ show last week's logged objects. """
    event._parsed.start = to_day(day()) - 24 * 60 * 60
    event._parsed.end = to_day(day())
    nr = 0
    for obj in db.selected(event):
        nr += 1
        event.display(obj, str(nr))

yesterday.perm = "USER"
