from multiprocessing import Process
import time
import os
import ladon.tools.log as log
from hashlib import sha1
from ladon.compat import PORTABLE_STRING

try:
    import cPickle
except:
    # Python 3
    import _pickle as cPickle

proc_id = os.getpid()

DEFAULT_TASK_TIMEOUT = 21600   # 6 hours


def cache_set(cache, key, val, timeout=DEFAULT_TASK_TIMEOUT):
    cache.set(key, cPickle.dumps(val), timeout)
    # print("SET", cache, key, val)


def cache_get(cache, key):
    val = cache.get(key)
    # print("GET", cache, key, val)
    return None if val is None else cPickle.loads(cache.get(key))


def cache_del(cache, key):
    cache.delete(key)


def next_task_id():
    global proc_id
    task_id = sha1()
    task_id.update(str(time.time()).encode('utf-8') + bytes(proc_id))
    return task_id.hexdigest()


def update_task_state(cache, task_id, running):
    cache_set(cache, "{}_state".format(task_id), running)


def task_running(cache, task_id):
    return cache_get(cache, "{}_state".format(task_id))


def set_task_info(cache, task_id, key, value):
    if task_running(cache, task_id) is not None:
        cache_set(cache, "{}_{}".format(task_id, key), value)


def get_task_info(cache, task_id, key):
    return cache_get(cache, "{}_{}".format(task_id, key))


def remove_task_info(cache, task_id, key=None):
    if key is None:
        for key_item in ['state', 'result', 'progress', 'exception', 'start', 'stop']:
            cache_del(cache, "{}_{}".format(task_id, key_item))
    else:
        cache_del(cache, "{}_{}".format(task_id, key))


class MultiProcessTaskContext(object):

    def __init__(self, cache_client, task_id):
        self.cache_client = cache_client
        self.task_id = PORTABLE_STRING(task_id, 'utf-8')

    def update_task_state(self, running):
        update_task_state(self.cache_client, self.task_id, running)

    def task_running(self):
        return task_running(self.cache_client, self.task_id)

    def get_task_info(self, key):
        return get_task_info(self.cache_client, self.task_id, key)

    def remove_task_info(self, key=None):
        return remove_task_info(self.cache_client, self.task_id, key)

    def set_task_info(self, key, val):
        set_task_info(self.cache_client, self.task_id, key, val)


class ManagedProcess(Process):
    def post_event(self, identifier, *args, **kw):
        if self.event_cb:
            self.event_cb(identifier, *args, **kw)

    def __init__(self, cache_client):
        self.task_id = next_task_id()
        if not getattr(self, 'event_cb', None):
            self.event_cb = None
        self.cache_client = cache_client
        super(ManagedProcess, self).__init__()

    def run_managed(self):
        raise NotImplementedError

    def run(self):
        update_task_state(self.cache_client, self.task_id, True)
        self.update_progress(0.0)
        self.set_task_info('start', time.time())
        try:
            self.run_managed()
        except:
            update_task_state(self.cache_client, self.task_id, False)
            log.write("Thread ID: %s (%s) failed with the following exception:\n%s" % (
                self.task_id, self.__class__, log.get_traceback()))
        self.set_task_info('stop', time.time())
        self.update_progress(1.0)
        update_task_state(self.cache_client, self.task_id, False)

    def update_progress(self, progress):
        if type(progress) != float:
            return
        if progress > 1:
            progress = 1
        if progress < 0:
            progress = 0
        self.set_task_info('progress', progress)

    def get_task_info(self, key):
        return get_task_info(self.cache_client, self.task_id, key)

    def set_task_info(self, key, val):
        set_task_info(self.cache_client, self.task_id, key, val)
