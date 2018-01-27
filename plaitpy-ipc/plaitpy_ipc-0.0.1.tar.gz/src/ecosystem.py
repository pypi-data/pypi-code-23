from . debug import *
from plaitpy import template

from sys import _getframe as getframe

import json
import random


def getID():
    # this function will print out the template_id of the caller (or his parent, maybe)
    i = 2
    errored_once = False
    while True:
        i+=1
        try:
            frame = getframe(i)
        except ValueError:
            i = 0
            if errored_once:
                return
            errored_once = True
            continue
        f_locals = frame.f_locals
        try:
            if issubclass(f_locals['self'].__class__, template.Template):
                template_id = id(f_locals['self'])
                return template_id
        except KeyError:
            pass

# a resource can be grabbed.
# it keeps track of who has grabbed it and
# who can grab it next
class LockResource(object):
    def __init__(self, ecosystem, name, **kwargs):
        self.owners = set()
        self.grabbed = set()

        self.name = name
        self.ecosystem = ecosystem
        type = kwargs.get("type", None)
        capacity = kwargs.get("capacity", 1)

        self.options = kwargs

        self.capacity = capacity
        self.type = type
        self.queue = {}
        self.next_queue = {}
        self.remaining = 0
        self.served = 0

    def turnover(self):
        prev_size = len(self.owners)
        self.owners = set()
        for g in self.grabbed:
            self.owners.add(g)

        released = max(prev_size - len(self.owners), 0)

        queue = []
        for r in self.next_queue:
            if r not in self.owners:
                queue.append((self.next_queue[r] - released, r))

        queue.sort()
        self.queue = dict(zip([q[1] for q in queue], range(len(queue))))
        self.next_queue = {}

        self.remaining = self.capacity - len(self.owners)
        self.grabbed = set()
        self.served = 0

    def grab(self):
        i = getID()
        ret = None
        if i in self.owners:
            ret = True
        elif self.remaining > 0:
            if len(self.queue):
                if i in self.queue:
                    if self.queue[i] <= self.remaining:
                        ret = True
            else:
                ret = True

            if ret:
                self.remaining -= 1


        if ret:
            self.grabbed.add(i)
            self.served += 1

            verbose(self.ecosystem.turn, "GRAB", self.name, "ID", i, "RET", ret)
            return ret

        if self.type == "queue":
            if i not in self.queue:
                self.next_queue[i] = len(self.queue) + 1
            else:
                self.next_queue[i] = self.queue[i]


class Ecosystem(object):
    def __init__(self, *args, **kwargs):
        from plaitpy.helpers import DotWrapper

        self.processes = set()
        self.turn = 0

        # TODO: do resources need to be namespaced?
        self.resources = {}

        # expired processes
        self.expired = {}
        self.dirty = False

        self.spawned = set()

        self.pid = 0
        self.pids = {}

    # the grab is our simplest primitive
    # a grab simulates a lock
    # it takes the lock one turn to "ungrab" itself,
    # so it is an "auto" unlock, instead of requiring a specific
    # call to unlock()
    def grab(self, resource_name, **kwargs):
        if resource_name not in self.resources:
            raise Exception("Resource undefined: %s" % resource_name)

        resource = self.resources[resource_name]
        return resource.grab()

    def add_resource(self, resource, **kwargs):
        # TODO: simulate several resource types:
        # fungibles: incr, decr
        # locks: grab, release
        # queues: wait until grabbed

        if resource in self.resources:
            return

        debug("ADDING RESOURCE:", resource, kwargs)
        type = kwargs.get("type", "").lower()
        if type == "lock":
            r = LockResource(self, resource, **kwargs)
        elif type == "queue":
            r = LockResource(self, resource, **kwargs)
        else:
            debug("UNKNOWN TYPE FOR RESOURCE", resource)
            from plaitpy.helpers import exit_error
            exit_error()

        self.resources[resource] = r

    def add_queue(self, resource, **kwargs):
        kwargs["type"] = "queue"
        self.add_resource(resource, **kwargs)

    def add_lock(self, resource, **kwargs):
        kwargs["type"] = "lock"
        self.add_resource(resource, **kwargs)

    def add_quantity(self, resource, value=0):
        self.resources[resource] = value


    def __add_process(self, process):
        self.pids[id(process)] = self.pid
        self.pid += 1
        self.spawned.add(process)

    def spawn(self, template_name, quiet=True):
        t = template.Template(template_name, quiet=quiet)
        verbose("SPAWNING PROCESS", template_name)
        self.__add_process(t)

    def expire(self, record=None):
        if record:
            i = record.get_id()
        else:
            i = getID()

        self.expired[i] = self.turn
        self.dirty = True
        return True

    def get_tick(self):
        return self.turn

    def get_pid(self, record=None):
        if record:
            i = record.get_id()
        else:
            i = getID()
        
        if i in self.pids:
            pid = self.pids[i]
        else:
            pid = self.pid
            self.pid += 1
            self.pids[i] = pid
        return pid

    def turnover(self):
        self.turn += 1

        if self.dirty:
            next_procs = set()
            for p in self.processes:
                if id(p) in self.expired:
                    debug("EXPIRED", id(p), self.pids[id(p)])
                    continue
                next_procs.add(p)
            self.processes = next_procs
            self.expired = {}

        for r in self.resources:
            if hasattr(self.resources[r], "turnover"):
                self.resources[r].turnover()

        for p in self.spawned:
            self.processes.add(p)
        self.spawned.clear()

        self.dirty = False

    def print_records(self, num_records):
        from plaitpy.template import print_record
        for ret in self.gen_record_batch(num_records):
            for r,proc in ret:
                print_record(proc, r)

    def gen_records(self):
        self.turnover()

        this_procs = [p for p in self.processes]
        if len(this_procs) > 1:
            random.shuffle(this_procs)
        for p in this_procs:
            try:
                r = p.gen_record()
            except Exception as e:
                debug("ERROR", e)
                from plaitpy.helpers import exit_error
                exit_error()


            yield r, p


    def gen_record_batch(self, num_records):
        for _ in range(num_records):
            self.turnover()

            ret = []

            this_procs = [p for p in self.processes]
            if len(this_procs) > 1:
                random.shuffle(this_procs)

            for p in this_procs:
                try:
                    r = p.gen_record()
                except Exception as e:
                    debug("ERROR", e)
                    from plaitpy.helpers import exit_error
                    exit_error()


                ret.append((r, p))

            yield ret

    def shared(self):
        return makeEcoWrapper(self)



def makeEcoWrapper(ECO):
    class EcoWrapper():
        def __getattr__(self, attr):
            if attr in ECO.resources:
                return ECO.resources[attr]

            if not attr in ECO.resources:
                from plaitpy.helpers import exit_error
                debug("MISSING ATTR", attr)
                exit_error()

        def __setattr__(self, attr, val):
            ECO.resources[attr] = val

    return EcoWrapper()
