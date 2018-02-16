"""
"""
from __future__ import division, print_function, unicode_literals
import Pyro4
import numbers
import sys

try:
    import numpy as np
except ImportError:
    import fake_numpy as np

if sys.version_info >= (3, 0):
    str_types = (str,)
else:
    str_types = (str, unicode)

class NeedsSubMeta(Exception):
    pass


@Pyro4.expose
class MetaProxy(object):
    #these are used for garbage collection
    protect = False
    done    = False

    def __init__(
            self,
            metaD,
            obj,
            register = True,
            protect  = None,
    ):
        self.metaD = metaD

        if isinstance(register, str_types):
            self.uri = self.metaD.daemon.register(self, register)
            if protect is None:
                protect = True
        elif register:
            #automatic registration!
            self.uri = self.metaD.daemon.register(self)

            if protect is None:
                protect = False
        else:
            self.uri = None
            if protect is None:
                protect = False

        #only assign in the rare event of True
        if protect:
            self.protect = protect

        self.obj = obj
        return

    def pyrometa_subsref(self, ref):
        #TODO
        raise NotImplementedError()

    def pyrometa_subsassgn(self, ref, val):
        #TODO
        raise NotImplementedError()

    def pyrometa_repr(self):
        return repr(self.obj)

    def pyrometa_str(self):
        return str(self.obj)

    def pyrometa_dir(self):
        dirlist = dir(self.obj)
        dirlist.sort()
        if self.protect:
            dirlist = [d for d in dirlist if not d.startswith('_')]
        return dirlist

    def pyrometa_getattr(self, name):
        checkname(self.obj, name)
        val = getattr(self.obj, name)
        return self.pyrometa_wrap(val)

    def pyrometa_setattr(self, name, val):
        checkname(self.obj, name)
        unval = self.pyrometa_unwrap(val)
        return setattr(self.obj, name, unval)

    def pyrometa_getitem(self, idx):
        idx = self.pyrometa_unwrap(idx)
        val = self.obj[idx]
        return self.pyrometa_wrap(val)

    def pyrometa_setitem(self, idx, val):
        idx = self.pyrometa_unwrap(idx)
        unval = self.pyrometa_unwrap(val)
        self.obj[idx] = unval
        return

    def pyrometa_call(self, name, *args, **kwargs):
        if name is None:
            val = self.obj
        else:
            checkname(self.obj, name)
            val = getattr(self.obj, name)
        unargs = self.pyrometa_unwrap(args)
        unkwargs = self.pyrometa_unwrap(kwargs)
        if check_MTsafe(val):
            with self.metaD.worker_sem:
                ret = val(*unargs, **unkwargs)
        else:
            with self.metaD.MTsafe:
                with self.metaD.worker_sem:
                    ret = val(*unargs, **unkwargs)
        return self.pyrometa_wrap(ret)

    @Pyro4.oneway
    def pyrometa_call_oneway(self, name, *args, **kwargs):
        if name is None:
            val = self.obj
        else:
            checkname(self.obj, name)
            val = getattr(self.obj, name)
        unargs = self.pyrometa_unwrap(args)
        unkwargs = self.pyrometa_unwrap(kwargs)
        if check_MTsafe(val):
            with self.metaD.worker_sem:
                ret = val(*unargs, **unkwargs)
        else:
            with self.metaD.MTsafe:
                with self.metaD.worker_sem:
                    ret = val(*unargs, **unkwargs)
        return

    def pyrometa_done(self):
        if not self.protect and self.done:
            raise RuntimeError("done set twice!")
        self.done = True

    def pyrometa_wrap(self, obj, throw = False):
        """
        throw causes an exception instead of creating a sub MetaProxy
        """
        if isinstance(obj, np.ndarray):
            return obj
        elif obj is None:
            return obj
        elif isinstance(obj, numbers.Number):
            return obj
        elif isinstance(obj, str_types):
            return obj
        elif isinstance(obj, list):
            try:
                sublist = [self.pyrometa_wrap(o, throw = True) for o in obj]
            except NeedsSubMeta:
                if throw:
                    raise
                else:
                    return MetaProxy(self.metaD, obj)
            else:
                return sublist
        elif isinstance(obj, tuple):
            try:
                subtup = tuple((self.pyrometa_wrap(o, throw = True) for o in obj))
            except NeedsSubMeta:
                if throw:
                    raise
                else:
                    return MetaProxy(self.metaD, obj)
            else:
                return subtup
        elif isinstance(obj, set):
            try:
                subset = set((self.pyrometa_wrap(o, throw = True) for o in obj))
            except NeedsSubMeta:
                if throw:
                    raise
                else:
                    return MetaProxy(self.metaD, obj)
            else:
                return subset
        elif isinstance(obj, dict):
            try:
                subdict = dict()
                for k, v in obj.items():
                    subdict[k] = self.pyrometa_wrap(v, throw = True)
            except NeedsSubMeta:
                if throw:
                    raise
                else:
                    return MetaProxy(self.metaD, obj)
            else:
                return subdict
        if throw:
            raise NeedsSubMeta()

        return MetaProxy(self.metaD, obj)

    def pyrometa_unwrap(self, obj):
        """
        throw causes an exception instead of creating a sub MetaProxy
        """
        if isinstance(obj, list):
            sublist = [self.pyrometa_unwrap(o) for o in obj]
            return sublist
        elif isinstance(obj, tuple):
            subtup = tuple((self.pyrometa_unwrap(o) for o in obj))
            return subtup
        elif isinstance(obj, set):
            subset = set((self.pyrometa_unwrap(o) for o in obj))
            return subset
        elif isinstance(obj, dict):
            subdict = dict()
            for k, v in obj.items():
                subdict[k] = self.pyrometa_unwrap(v)
            return subdict
        elif isinstance(obj, MetaProxy):
            return obj.obj
        elif isinstance(obj, Pyro4.Proxy):
            uri = obj._pyroUri
            obj = self.metaD.uri2obj(uri)
            if isinstance(obj, MetaProxy):
                return obj.obj
            else:
                return obj
        else:
            return obj


def checkname(obj, name):
    if name.startswith('_'):
        try:
            allow = obj._msurrogate_unsafe
        except AttributeError:
            allow = False
        if not allow:
            raise AttributeError('attributes/methods starting with _ not allowed')

def check_MTsafe(obj):
    """
    Recurse up object and parents via __self__ of instancemethod types in search of an obj._msurrogate_MT flag indicating to use full multithreading
    """
    #TODO, could do isinstance checks against types.FunctionType and types.MethodType, but those seem to carry __self__
    while True:
        try:
            safe = obj._msurrogate_MT
        except AttributeError:
            pass
        else:
            return safe

        try:
            parent = obj.__self__
        except AttributeError:
            return False
        obj = parent
