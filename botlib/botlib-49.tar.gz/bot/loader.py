# BOTLIB - Framework to program bots !!
#
# ldr.py (loader)
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

""" load modules. """

from bot.event import Event
from bot.obj import Default, Object
from bot.register import Register

import importlib
import logging
import os
import pkgutil
import types
import sys

class ELOCATE(Exception):
    """ the given path does not point to a module. """
    pass
    
class Loader(Default):

    """
        A Handler handles events pushed to it. Handlers can be threaded,
        e.g. start a thread on every event received, or not threaded in which
        case the event is handeled in loop.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cbs = Register()
        self._cmds = []
        self._descriptions = Object()
        self._handlers = Register()
        self._modnames = []
        self._names = Register()
        self._table = Object()

    def direct(self, name, package=None, log=False):
        """ import a module directly, not storing it in the cache. """
        log and logging.warn("direct %s" % name)
        mod = importlib.import_module(name, package)
        return mod

    def get_cbs(self, cmnd):
        cbs = self._cbs.get(cmnd, [])
        all = self._cbs.get("ALL", [])
        cbs.extend(all)
        return cbs

    def get_handlers(self, cmnd):
        """ search for a function registered by command. """
        if cmnd not in self._handlers:
            for modname in self._names.get(cmnd, []):
                self.load_mod(modname, force=True, log=True)
        funcs = self._handlers.get(cmnd, [])
        return funcs

    def list(self, name):
        """ list all functions found in a module. """
        for modname in self.modules(name):
            mod = self.load_mod(modname)
            for key in dir(mod):
                obj = getattr(mod, key, None)
                if obj and type(obj) == types.FunctionType:
                    if "event" in obj.__code__.co_varnames:
                        yield key

    def load_file(self, name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None:
            raise ELOCATE(path)
        else:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            sys.modules[name] = module
            self.scan(name, module)
            return module

    def load_mod(self, modname, force=False, log=True):
        """ load a module. """
        if force or modname not in self._table:
            self._table[modname] = self.direct(modname, log=log)
        elif modname in self._table:
            return self._table[modname]
        return self.scan(modname, self._table[modname])
        
    def scan(self, name, module):
        """ scan a module for func(event) functios and register them on _handlers as a command/callback combination. """
        for key in dir(module):
            if key.startswith("_"):
                continue
            obj = getattr(module, key, None)
            if obj and type(obj) == types.FunctionType:
                if "__wrapped__" in dir(obj):
                    func = obj.__wrapped__
                else:
                    func = obj
                if "event" in func.__code__.co_varnames:
                    self._names.register(key, name)
                    self._handlers.register(key, obj)
                    self._cmds.append(key)
                    if name not in self._modnames:
                        self._modnames.append(name)
                    if "__doc__" in dir(obj):
                        if obj.__doc__:
                            self._descriptions.register(key, obj.__doc__.strip(), True)
        return module

    def services(self, cfg):
        for name in cfg.init.split(","):
            if not name:
                continue
            e = Event(cfg)
            e.txt = "start %s" % name
            e.origin = "root@shell"
            e.server = cfg.server or "localhost"
            e.channel = cfg.channel or "#botlib"
            e.nick = cfg.nick or "botlib"
            e.dispatch()

    def modules(self, name):
        """ return a list of modules in the named packages or cfg.packages if no module name is provided. """
        package = self.load_mod(name)
        for pkg in pkgutil.walk_packages(package.__path__, name + "."):
            yield pkg[1]

    def prep(self, event):
        """ match command with it's function. """
        event.parse()
        event._cbs = self.get_cbs(event.cb)
        event._funcs = self.get_handlers(event._parsed.command or event._parsed.cmnd)
        for func in event._funcs:
            if "_threaded" in dir(func) and func._threaded:
                event._threaded = True
                break

    def reload(self, name, force=True, event=None):
        """ reload module. """
        if not force:
            self._table[name].reload()
        else:
            self.load_mod(name, force=force)

    def register(self, key, val, force=False):
        """ register a handler. """
        self._handlers.register(key, val, force=force)

    def walk(self, name, init=False, force=False, log=False):
        """ return all modules in a package. """
        for modname in sorted(list(self.modules(name))):
            self.load_mod(modname, force, log)
