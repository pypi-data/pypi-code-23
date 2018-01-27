"""
"""
from __future__ import division, print_function, unicode_literals
import Pyro4
import threading
import contextlib

from . import meta_proxy


class MetaDaemon(object):

    def __init__(
        self,
        daemon = None,
        workers_N = 1,
    ):
        if daemon is None:
            daemon = Pyro4.Daemon()

        self.daemon = daemon
        self._worker_sem_value = None
        self.workers_N_set(workers_N)
        self.MTsafe = threading.Lock()

        #for caching GC
        self._metas_done = dict()

        #name -> object
        #to be wrapped and started in daemon
        self._objects = {}
        self._name_uri_reg = dict()

        #URI -> metaproxy(object) registry for json
        self._uri_registry = {}
        self._name_registry = {}
        return

    def workers_N_set(self, workers_N):
        #capture the remaining uses of the semaphore
        #if self._worker_sem_value is not None:
        #    for idx in range(self._worker_sem_value - 1):
        #        self.worker_sem.acquire()
        if workers_N is not None:
            self.worker_sem = threading.Semaphore(workers_N)
        else:
            #only used via the "with" interface, so this is OK
            @contextlib.contextmanager
            def fake_lock():
                yield
            fake_lock.acquire = lambda : None
            fake_lock.release = lambda : None
            self.worker_sem = fake_lock

    def register(
            self,
            obj    = None,
            name   = None,
            remove = False,
    ):
        if not remove:
            assert(obj is not None)
            if name is None:
                name = obj.__name__

            meta_object = meta_proxy.MetaProxy(self, obj, register = name)
            uri = str(meta_object.uri)

            self._objects[name] = obj
            self._uri_registry[uri] = meta_object
            self._name_registry[name] = meta_object
            self._name_uri_reg[name] = uri
        else:
            if name is None:
                assert(obj is not None)
                name = obj.__name__
            meta_obj = self._name_registry[name]
            obj_reg = self._objects[name]
            if obj is not None:
                assert(obj is obj_reg)

            del self._objects[name]
            del self._name_registry[name]
            del self._uri_registry[meta_obj.uri]
            del self._name_uri_reg[name]
            self.daemon.unregister(name)

    def uri2obj(self, uri):
        uri = str(uri)
        name, loc = uri.split('@')
        if not name.startswith('PYRO:'):
            raise RuntimeError("Proxy unwrapping can't recognize proxy")
        name = name[5:]
        obj = self.daemon.objectsById[name]
        return obj

    def workspace_dict(self):
        d = dict()
        for k, v in self._name_uri_reg.items():
            d[k] = str(v)
        return d

    def workspace_reset(self):
        #TODO
        temp = dict(self.daemon.objectsById)
        for k, v in temp.items():
            if k not in self._objects:
                self.daemon.unregister(k)
        return

    def workspace_gc(self):
        for k, v in self._metas_done.items():
            self.daemon.unregister(k)
        self._metas_done = dict()
        self.workspace_counts()
        for k, v in self._metas_done.items():
            self.daemon.unregister(k)
        self._metas_done = dict()
        return len(self.daemon.objectsById)

    def workspace_counts(self):
        #temp is for threadsafety
        temp = dict(self.daemon.objectsById)
        for k, v in temp.items():
            if isinstance(v, meta_proxy.MetaProxy):
                if not v.protect and v.done:
                    self._metas_done[k] = v
        return len(self._metas_done), len(self.temp)

    def workspace_close(self):
        self.daemon.shutdown()

