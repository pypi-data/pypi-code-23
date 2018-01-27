# BOTLIB - Framework to program bots !!
#
# obj.py (object)
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

"""
    object class to save/load json files.

    use the save mathod to sync an object to disk.

    >>> o = Object()
    >>> o.save()


    if a pathname is not provided a timestamp filename is provided, for example:

    ::

        '/home/bart/.bot/object/2018-01-20/17:23:40.327227'


    use the load method to load an Object from disk.
    
    >>> o = Object()
    >>> o.load("config/new")

    the cfg.workdir variable in this module is prepended to a filename.

    >>> o._container.path


"""

__version__ = "3"

import _thread
import datetime
import fcntl
import hashlib
import json
import logging
import optparse
import os
import string
import time
import threading

class ESET(Exception):
    """
         the provided string is not JSON.

    """
    pass

class EJSON(Exception):
    """
         the provided string is not JSON.

    """
    pass

class ENOJSON(Exception):
    """
         the provided string is not JSON.

    """
    pass
    
class EBORDER(Exception):
    """
        attemped to write outside of the workdir.

    """
    pass

class EFILENAME(Exception):
    """
        provided string is not a filename.

    """
    pass

class ENOTSET(Exception):
    """
        variable is not set.

    """
    pass

def locked(func, *args, **kwargs):

    """
        locked decorator, use to lock decorator function.

    """

    lock = _thread.allocate_lock()

    def lockedfunc(*args, **kwargs):
        """
            lockded function to wrap a function in.

        """
        lock.acquire()
        res = None
        try:
            res = func(*args, **kwargs)
        finally:
            try:
                lock.release()
            except:
                pass
        return res
    return lockedfunc

class Object(dict):

    """
        save/load object's state to timestamped json string file..

    """

    def __getattribute__(self, name):
        """
            get attribute and, if that fails, check item access.
            
            >>> o = Object({"key1": "value1"})
            >>> o.key1

        """
        try:
            return super().__getattribute__(name)
        except AttributeError:
            try:
                return self[name]
            except KeyError:
                raise AttributeError(name)

    def __getattr__(self, name):
        """
            get missing attribute by name.
            
            >>> o = Object()
            >>> o._container # meta data such pathname etc.
            >>> o._ready     # event set when object is finished
            >>> o._thrs      # threads started when processing this object

        """
        if name == "_container":
            self._container = Object()
        if name == "_ready":
            self._ready = threading.Event()
        if name == "_thrs":
            self._thrs = []
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)
            
    def __repr__(self):
        """
            mimic a normal __repr__.
            
            >>> o = Object()
            >>> repr(o)

        """
        return '<%s.%s at %s>' % (
            self.__class__.__module__,
            self.__class__.__name__,
            hex(id(self))
        )

    def __setattr__(self, name, value):
        """
            implement dotted dict access.

            >>> o = Object()
            >>> o.key1 = "value1"

        """
        return self.__setitem__(name, value)

    def __str__(self):
        """
            return a pretyified json string.

            >>> o = Object()
            >>> print(o)

        """
        return self.nice()

    def cache(self, path: str):
        """
            load this object from cache or read it from disk.

            >>> o = Object()
            >>> o.cache("config/cli")

            returns:
                Object: loaded from cache or disk

        """
        if path in cache:
            return cache[path]
        return self.load(path)

    def clear(self) -> None:
        """
            clear the ready flag.

            >>> o = Object()
            >>> o.clear()

        """
        self._ready.clear()

    def format(self, keys=[], skip=[], nokeys=False, reverse=False) -> str:
        """
            return a displayable string from a list of attributes.

            >>> o = Object({"key1": "test1", "key2": "test2"})
            >>> o.format()              # use all keys
            >>> o.format(["key1"])      # only show key1 and it's corresponding value
            >>> o.format(skip=["key2"]) # skip key2
            >>> o.format(nokeys=True)   # don't display keys
            >>> o.format(reverse=True)  # display last key first
   
        """
        keys = keys or self.keys()
        if reverse:
            keys = reversed(list(keys))
        result = []
        for key in reversed(list(keys)):
            if key == "default":
                continue
            if key.startswith("_"):
                continue
            if key in skip:
                continue
            if nokeys:
                result.append("%-8s" % str(self[key]))
            else:
                result.append("%10s" % "%s=%s" % (key, str(self[key])))
        txt = " ".join(result)
        return txt.rstrip()

    def grep(self, val: str):
        """
            return a new Object with the values that match provided val argument.

            >>> o = Object({"key1", "value1"})
            >>> o.grep("key")

            returns:
                Object: new Object with grepped items
                
        """
        o = Object()
        for key, value in self.items():
            if val in str(value) and value not in o:
                o[key] = value
        return o

    def isSet(self) -> bool:
        """
            check whether ready flag is set.
       
            >>> o = Object()
            >>> o.isSet()
                  
        """
        return self._ready.isSet()

    def load(self, path: str, force=False, skip=[], full=True):
        """
            load a json file into this object. use skip as a list of keys to skip.

            >>> o = Object()
            >>> o.load("test")

            returns:
                Object: pointer to self

        """
        if not cfg.workdir in path:
            path = os.path.join(cfg.workdir, path)
        logging.debug("load %s" % os.sep.join(path.split(os.sep)[-3:]))
        ondisk = self.read(path)
        self._container.path = path
        fromdisk = json.loads(ondisk)
        if "signature" in fromdisk:
            if not verify_signature(fromdisk["data"], fromdisk["signature"]) and not force:
                logging.warn("mismatch %s" % os.sep.join(path.split(os.sep)[-3:]))
        if "data" in fromdisk:
            self.update(slice(fromdisk["data"], skip=skip, full=full)) 
            self._container.update(slice(fromdisk, skip=["data"]))
        cache[path] = self
        return self

    def loads(self, jsonstring: str):
        """
            update with deconstructed (dict) json string.

            >>> o = Object()
            >>> o.loads('{"key1": "value1"}')

            returns:
                Object: pointer to self

        """
        self.update(json.loads(jsonstring))
        return self

    def merge(self, obj):
        """
            merge an object into this on, only set keys that are already present.

            >>> o = Object()
            >>> o.merge({"key1": "value1"})

            returns:
                Object: pointer merged self

        """
        for k, v in obj.items():
            if v:
                self[k] = v
        return self

    def nice(self) -> str:
        """
            return a nicyfied JSON dump.

            >>> o = Object({"key1": "value1"})
            >>> o.nice()
            
        """
        return json.dumps(self, default=smooth, indent=4, sort_keys=True)

    def pure(self) -> str:
        """
            return a sliced (no _ keys), indent=4, sort_key is True, json dump.
            
            >>> o = Object()
            >>> o.pure()
            
        """
        return json.dumps(slice(self, full=False), indent=4, sort_keys=True)

    def prepare(self) -> str:
        """
            prepare the object and return a string containing the "data" part.

            >>> o = Object({"key1": "value1"})
            >>> o.prepare()

        """
        todisk = Object()
        todisk.data = dumped(slice(self, skip=["_container", "_parsed"], full=True))
        todisk.data.__typed__ = str(type(self))
        if "prefix" not in todisk:
            todisk.prefix = get_prefix(self)
        todisk.saved = time.ctime(time.time())
        try:
            todisk.signature = make_signature(todisk["data"])
        except:
            pass
        try:
            result = json.dumps(todisk, default=smooth, indent=4, ensure_ascii=False, sort_keys=True)
        except TypeError:
            raise ENOJSON(todisk.prefix)
        return result

    def read(self, path: str) -> str:
        """
             read a json dump from given path, returning the json string with comments stripped.

             >>> o = Object()
             >>> o.read("config/cli")

        """
        try:
            f = open(path, "r", encoding="utf-8")
        except FileNotFoundError:
            return "{}"
        res = ""
        for line in f:
            if not line.strip().startswith("#"):
                res += line
        if not res.strip():
            return "{}"
        f.close()
        return res

    def ready(self) -> bool:
        """ signal this object as "ready". """
        return self._ready.set()
        
    def register(self, key, val, force=False) -> None:
        """
            register key, value .. throw an exception if key is already set.

            >>> o = Object()
            >>> o.register("key1", "value1")

        """
        if key in self and not force:
            raise ESET(key)
        self[key] = val
        
    def save(self, path="", **kwargs) -> str:
        """
            save a static (fix filepath) version of this object.

            >>> o = Object()
            >>> o.save()	# pathname is initialised with a timestamped filename
            >>> o.save("test")	# pathname is provided

        """
        return self.sync(path=path, **kwargs)

    def search(self, name:str):
        """
            search this objects keys skipping keys that start with "_".

            >>> o = Object({"key1", "value1"})
            >>> o.search("key")
                
            retiurns:
                Object: new Object with searched items.

        """
        o = Object()
        for key, value in self.items():
            if key.startswith("_"):
                continue
            if key in name:
                o[key] = value
            elif name in key.split(".")[-1]:
                o[key] = value
        return o

    def sync(self, path="", **kwargs) -> str:
        """
            sync to disk using provided/created path. this sync() method does the real saving to disk.

            >>> o = Object()
            >>> o.sync()
            >>> o.sync("test/test1')

        """
        if not path:
            path = get_path(self)
        if not path:
            wd = kwargs.get("workdir", cfg.workdir)
            path = os.path.join(wd, get_prefix(self))
            stime = kwargs.get("stime", None)
            if stime:
                path = os.path.join(path, stime)
            else:
                path = os.path.join(path, rtime())
        if cfg.workdir not in path:
            p = path.split(os.sep)[-2:]
            got = os.sep.join(p)
            path = os.path.join(cfg.workdir, got)
        path = os.path.abspath(os.path.normpath(path))
        if cfg.workdir not in path:
            raise EBORDER(path)
        if not allowchar(path):
            raise EFILENAME(path)
        logging.info("sync %s" % os.sep.join(path.split(os.sep)[-3:]))
        self._container.path = path
        self._container.saved = time.ctime()
        d, fn = os.path.split(path)
        if not os.path.exists(d):
            cdir(d)
        todisk = self.prepare()
        rpath = path + "_tmp"
        try:
            datafile = open(rpath, 'w')
            fcntl.flock(datafile, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            datafile = open(rpath, 'w')
            fcntl.flock(datafile, fcntl.LOCK_EX | fcntl.LOCK_NB)
        datafile.write(headertxt % ("%s characters" % len(todisk), time.ctime(time.time())))
        datafile.write(todisk)
        datafile.write("\n")
        datafile.flush()
        os.rename(rpath, path)
        fcntl.flock(datafile, fcntl.LOCK_UN)
        datafile.close()
        return path

    def upgrade(self, input: dict):
        """
            upgrade this object with a dictionary, only setting attributes if they do not exist.

            >>> o = Object()
            >>> o.upgrade({"key1": "value1"})
            >>> o.upgrade({"key1`": "value2"})

            returns:
                 Object: pointer to upgraded self

        """
        for k, v in input.items():
            if k.startswith("_"):
                continue
            if k in self:
                if not self[k]:
                    self[k] = input[k]
        return self

    def wait(self, timeout=None) -> list:
        """
            wait for this object's ready flag and join all thread that have been started in handling this object,

            >>> o = Object()
            >>> o.wait()
            >>> o.wait(10.0) # blocks for 10 seconds                

        """
        result = []
        self._ready.wait(timeout)
        for thr in self._thrs:
            try:
                res = thr.join(timeout)
                result.append(res)
                self._thrs.remove(thr)
            except RuntimeError:
                pass
        return result

class Default(Object):

    """
        object with a "default" value. standard default return is Object().

    """

    def __init__(self, *args, **kwargs):
        Object.__init__(self, *args, **kwargs)
        self._default = kwargs.get("default", "")

    def __getattr__(self, name):
        """
            override Object.__getattr__.

        """
        try:
            return super().__getattr__(name)
        except (AttributeError, KeyError):
            self[name] = self["_default"]
        return self[name]

class Config(Default):

    """
        config class with a empty string as default.

    """

    def fromdisk(self, name, tpl={}):
        """
            load the config from file
        """
        self.update(tpl)
        self.cache(os.path.join(cfg.workdir, "config", name))
        return self


cfg = Config()
cfg.workdir = os.path.join(os.path.expanduser("~"), ".obj")

def allowchar(s):
    """
        check if s is a allowed filename string.
        
    """
    res = False
    for i in s:
        if i in allowedchars:
            res = True
        else:
            res = False
    return res

def cdir(path):
    """
        create a directory.

    """
    res = ""
    for p in path.split(os.sep):
        res += "%s%s" % (p, os.sep)
        padje = os.path.abspath(os.path.normpath(res))
        try:
            os.mkdir(padje)
        except (IsADirectoryError, NotADirectoryError, FileExistsError):
            pass
        except OSError as ex:
            logging.error(get_exception())
    return True

def dumped(o):
    """
        add type string to an object attributes.

    """
    t = type(o)
    if t == str:
        return o
    if t in [list, tuple]:
        l = []
        for obj in o:
            l.append(dumped(obj))
        return l
    if "items" not in dir(o):
        return o
    oo = t()
    for k, v in o.items():
        try:
            v["__typed__"] = str(type(v))
        except:
            pass
        oo[k] = dumped(v)
    return oo

def fromstring(txt):
    """
        derive an object from the repr string.

    """
    if " at " in txt:
        txt = txt.split(" at ")[0]
    if " of " in txt:
        t1, t2 = txt.split(" of ")
        txt = t2.split(".")[-1] + "." + t1.split(".")[-1]
    if "," in txt:
        txt = txt.split(",")[0]
    txt = txt.replace("<function ", "")
    return txt.strip()

def get_prefix(obj):
    """
        return the object's prefix.

    """
    return name(obj).split(".")[-1].lower()

def get_path(obj):
    """
        return the path used to store the object's json dump.

    """
    try:
        return obj._container.path
    except:
        pass

def get_saved(obj):
    """
        return the saved attribue of an object.

    """
    p = ""
    if "_container" in obj:
        p = getattr(obj._container, "saved", "")
        if p:
            return p


def make_signature(obj):
    """
         make an signature based on the values of an object.

    """
    data = json.dumps(obj, indent=4, ensure_ascii=True, sort_keys=True)
    return str(hashlib.sha1(bytes(str(data), "utf-8")).hexdigest())

def name(obj):
    """
         return the name destilled from the repr of an object.

    """
    txt = repr(obj)
    return fromstring(txt)

def rtime():
    """
        return a filestamp usable in a filename.

    """
    res =  str(datetime.datetime.now()).replace(" ", os.sep)
    return res

def slice(obj, keys=[], skip=[], full=True, skipempty=True):
    """
        return a slice of an object.

    """
    t = type(obj)
    o = t()
    if not keys:
        keys = obj.keys()
    for key in keys:
        if key in skip:
            continue
        if not full and key.startswith("_"):
            continue
        val = obj.get(key, None)
        if skipempty and not val:
            continue
        if val and "keys" in dir(val):
            o[key] = slice(val, skip=skip, full=full, skipempty=skipempty)
        else:
            o[key] = val
    return o

def smooth(obj):
    """
        return a JSON representation of an object.

    """
    if type(obj) not in basic_types:
        return repr(obj)
    return obj

def verify_signature(obj, signature):
    """
        verify an object's integrty based on the object's signature.

    """
    signature2 = make_signature(obj)
    return signature2 == signature

cache = Object()
nodict_types = [str, int, float, bool, None]
basic_types = [dict, list, str, int, float, bool, None]
allowedchars = string.ascii_letters + string.digits + '_+/$.-'

headertxt = '''# this is a botlib file, %s
#
# botlib can edit this file !!
#
# saved on %s
'''
