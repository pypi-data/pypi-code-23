from threading import Lock, Thread
import time
import ladon.tools.log as log
from hashlib import sha1


thread_id_locker = Lock()
common_lock = Lock()

thread_dict = {
    'running': [],
    'done': [],
    'thread_info': {}
}

thread_id_counter = 0


def next_task_id():
    global thread_id_counter, thread_id_locker
    thread_id_locker.acquire()
    thread_id_counter += 1
    thread_id_locker.release()
    task_id = sha1()
    task_id.update(str(time.time()).encode('utf-8') + bytes(thread_id_counter))
    return task_id.hexdigest()


def update_task_state(thread_id, running):
    global thread_dict, common_lock
    common_lock.acquire()
    if running:
        if thread_id not in thread_dict['running']:
            thread_dict['running'] += [thread_id]
            try:
                thread_dict['done'].remove(thread_id)
            except ValueError as e:
                pass
    else:
        if thread_id not in thread_dict['done']:
            thread_dict['done'] += [thread_id]
            try:
                thread_dict['running'].remove(thread_id)
            except ValueError as e:
                pass

    common_lock.release()


def task_running(thread_id):
    global thread_dict, common_lock
    common_lock.acquire()
    running = thread_id in thread_dict['running']
    common_lock.release()
    return running


def set_task_info(thread_id, key, value):
    global thread_dict, common_lock
    common_lock.acquire()
    if thread_id not in thread_dict['thread_info']:
        thread_dict['thread_info'][thread_id] = {}
    thread_dict['thread_info'][thread_id][key] = value
    common_lock.release()


def remove_task_info(thread_id, key):
    global thread_dict, common_lock
    success = False
    common_lock.acquire()
    if thread_id in thread_dict['thread_info']:
        try:
            del thread_dict['thread_info'][thread_id][key]
            success = True
        except KeyError:
            pass
    common_lock.release()
    return success


def get_task_info(thread_id, key):
    global thread_dict, common_lock
    common_lock.acquire()
    val = thread_dict['thread_info'].get(thread_id, {}).get(key, None)
    common_lock.release()
    return val


class ThreadedTaskContext(object):

    def __init__(self, thread_id):
        self.thread_id = thread_id

    def update_task_state(self, running):
        update_task_state(self.thread_id, running)

    def task_running(self):
        return task_running(self.thread_id)

    def get_task_info(self, key):
        return get_task_info(self.thread_id, key)

    def remove_task_info(self, key):
        return remove_task_info(self.thread_id, key)

    def set_task_info(self, key, val):
        set_task_info(self.thread_id, key, val)


class ManagedThread(Thread):
    def post_event(self, identifier, *args, **kw):
        if self.event_cb:
            self.event_cb(identifier, *args, **kw)

    def __init__(self):
        self.task_id = next_task_id().encode('utf-8')
        if not getattr(self, 'event_cb', None):
            self.event_cb = None
        super(ManagedThread, self).__init__()

    def run_managed(self):
        raise NotImplementedError

    def run(self):
        update_task_state(self.task_id, True)
        self.update_progress(0.0)
        self.set_task_info('start', time.time())
        try:
            self.run_managed()
        except:
            update_task_state(self.task_id, False)
            log.write("Thread ID: %s (%s) failed with the following exception:\n%s" % (
                self.task_id, self.__class__, log.get_traceback()))
        self.set_task_info('stop', time.time())
        self.update_progress(1.0)
        update_task_state(self.task_id, False)

    def update_progress(self, progress):
        if type(progress) != float:
            return
        if progress > 1:
            progress = 1
        if progress < 0:
            progress = 0
        self.set_task_info('progress', progress)

    def set_task_info(self, key, val):
        set_task_info(self.task_id, key, val)
