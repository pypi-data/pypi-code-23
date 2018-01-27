# BOTLIB - Framework to program bots !!
#
# db.py (databases)
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

""" access saved json files. """

from bot.obj import Default, Object, cdir, ENOTSET
from bot.register import Register
from bot.utils.time import fn_time, to_day

import logging
import time
import os

class Db(Object):

    """ database object managing JSON files. """

    def attr(self, prefix):
        """ return prefixes or last prefixed object. """
        obj = self.last(prefix)
        res = []
        if obj:
            res = obj.keys()
        return res

    def find(self, prefix, *args, **kwargs):
        """ find all objects stored with a prefix subdirectory. """
        for fn in self.prefixed(prefix, *args):
            obj = Object().cache(fn)
            if "deleted" in obj and obj.deleted:
                continue
            p = obj.get(prefix, "")
            if args and args[0] not in p:
                continue
            yield obj

    def first(self, *args, **kwargs):
        """ return first object matching provided prefix. """
        prefix = args[0]
        prefixes = self.prefixed(*args, **kwargs)
        for p in prefixes:
            if prefix not in p:
                continue
            return Object().cache(p)

    def is_prefix(self, prefix):
        """ chech whether prefix (subdirectory in the workdir) exists.  """
        from bot.obj import workdir
        for p in os.listdir(workdir):
            if prefix in p:
                return True

    def last(self, *args, **kwargs):
        """ return last record with a matching prefix. """
        prefix = args[0]
        if len(args) > 1:
            value = args[1]
        else:
            value = ""
        paths = self.prefixed(prefix, **kwargs)
        for p in paths[::-1]:
            if value and value not in p:
                continue
            return Object().cache(p)

    def prefixed(self, *args, **kwargs):
        """ return all filename in a workdir subdirectory, the 'prefix'. """
        from bot.obj import cfg
        if not args:
            return []
        files = []
        if args[0] not in self.prefixes():
            return []
        path = os.path.normpath(os.path.join(cfg.workdir, args[0]))
        for fn in self.scan(path, *args, **kwargs):
            files.append(fn)
        return sorted(files, key=lambda x: fn_time(x))

    def prefixes(self):
        """ show prefixs (toplevel directories) in the workdir. """
        from bot.obj import cfg
        if not os.path.exists(cfg.workdir):
            cdir(cfg.workdir)
        for p in os.listdir(os.path.normpath(cfg.workdir)):
            yield p

    def scan(self, path, *args, **kwargs):
        """ scan all files. """
        p = Default(kwargs, default="")
        if not path.endswith(os.sep):
            path += os.sep
        result = []
        for rootdir, dirs, files in os.walk(path, topdown=True):
            if not os.path.isdir(rootdir):
                continue
            for fn in files:
                fnn = os.path.join(rootdir, fn)
                timed = fn_time(fnn)
                if timed and p.start and timed < p.start:
                    continue
                if timed and p.end and timed > p.end:
                    continue
                yield fnn

    def selected(self, event):
        """ select objects based on a _parsed event. """
        seen = []
        thrs = []
        if not event._parsed.args:
            return []
        starttime = time.time()
        nr = -1
        index = event._parsed.index
        if not event._parsed.start:
            if event._parsed.delta:
                event._parsed.start = time.time() + (event._parsed.delta * 60*60)
                event._parsed.end = time.time()
        got_uniqs = Register()
        for fn in self.prefixed(*event._parsed.args, **event._parsed):
            obj = self.selector(event, fn, got_uniqs)
            if obj:
                nr += 1
                if index != None and nr != index:
                    continue
                yield obj
        endtime = time.time()

    def selector(self, event, fn, uniqs, obj=None):
        """ select objects matching the _parsed fields in the event object. """
        from bot.utils.db import selector, notwanted, wanted, ignore, uniq
        if not obj:
            obj = Object().cache(fn)
        if "nodel" not in event and "deleted" in obj and obj.deleted:
            return
        if not selector(obj, event._parsed.fields):
            return
        if notwanted(obj, event._parsed.notwant):
            return
        if not wanted(obj, event._parsed.want):
            return
        if ignore(obj, event._parsed.ignore):
            return
        if event._parsed.uniqs and not uniq(obj, event._parsed.uniqs, uniqs):
            return
        return obj

    def sequence(self, prefix, start, end=time.time(), skip=[]):
        """ select objects of type prefix, start time till end time. """
        p = Object()
        p.start = start
        p.end = end
        for fn in self.prefixed(prefix, **p):
            do_skip = False
            for k in skip:
                if k in fn:
                    do_skip = True
            if do_skip:
                continue
            try:
                e = Object().cache(fn)
            except Exception as ex:
                logging.warn("fail %s %s" % (fn, str(ex)))
                continue
            yield e

    def since(self, start, *args, **kwargs):
        """ return all objects since a given time. """
        e = Object(**kwargs)
        e.start = parse_time(start)
        for fn in self.prefixed(*args, **e):
            try:
                obj = Object().cache(fn)
            except Exception as ex:
                logging.warn("fail %s %s" % (fn, str(ex)))
                continue
            if "deleted" in obj and obj.deleted:
                continue
            yield obj

