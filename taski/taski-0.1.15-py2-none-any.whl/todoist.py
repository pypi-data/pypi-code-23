""" Todoist adapter """

import pickle
import os
import time
import glob
import uuid
import json
import math
import re
from datetime import datetime
from pytodoist import todoist
from base import dlog, Project, Task
from util import same_date


TO_UPDATE = {}


class FileCache(object):
    """
    FileCache General file cache backed by pickle. Cache files are located under
    "/tmp/[name].data".
    """
    def __init__(self):
        self.ttl = 3600 # seconds

    def get(self, key):
        """
        Get an object from file cache. Returns `none` if `key` is not
        in cache
        """
        try:
            key = key.replace("/", "_")
            fname = "/tmp/" + key + ".data"
            ctime = os.stat(fname).st_ctime
            #print("st_ctime: ", t)
            now = time.time()
            if now - ctime > self.ttl:
                dlog("ttl expired for file: " + fname)
                return None

            f = open(fname)
            r = pickle.load(f)
            f.close()
            return r
        except IOError as err:
            dlog(str(err))
            return None
        except OSError as err:
            dlog(str(err))
            return None

    def set(self, key, value):
        """
        Set an object from file cache. Returns `False` for failure and `True`
        for success
        """
        try:
            key = key.replace("/", "_")
            fname = "/tmp/" + key + ".data"
            f = open(fname, "wb")
            pickle.dump(value, f)
            f.close()
        except IOError as err:
            dlog(err)
            return False
        return True

    def clear(self):
        cache_files = glob.glob("/tmp/*.data")
        for f in cache_files:
            dlog("unlink: " + f)
            os.unlink(f)

class Todoist():
    def __init__(self):
        self.user = None
        self.fc = None
        self.completed_tasks = None
        self.planned_label = None
        self.planned_label_id = None
        self.already_planned = []

    def init(self, cfg):
        self.fc = FileCache()
        self.user = todoist.login(cfg["email"], cfg["password"])
        self.planned_label = self.user.get_label("planned")
        if not self.planned_label:
            self.planned_label = self.user.add_label("planned")
        self.planned_label_id = self.planned_label.id

    def PyTaskAdapter(self, pytodoist_task):
        t = Task()
        tt = pytodoist_task
        t.id = tt.id
        t.name = tt.content
        t.done = tt.checked
        t.pid = tt.project_id
        t._data = tt
        if hasattr(tt, "completed_date"):
            t.ts_done = datetime.strptime(tt.completed_date, "%a %d %b %Y %H:%M:%S +0000")
            t.done = True

        return t

    def get_command(self, user, command_type, command_args):
	command = {
            'type': command_type,
            'args': command_args,
            'uuid': str(uuid.uuid4()),
            'temp_id': str(uuid.uuid4())
        }
	#commands = json.dumps([command])
	return command

    def manually_planned(self, ttask):
        pass

    def get_ttasks(self):
        ttasks = self.fc.get("ttasks")
        if ttasks is None:
            dlog("ttasks MISS")
            ttasks = self.user.get_tasks()
            self.fc.set("ttasks", ttasks)
        else:
            dlog("ttasks cache HIT")
        return ttasks

    def get_projects(self):
        ttasks = self.get_ttasks()
        ttasks = sorted(ttasks, key=lambda x:x.item_order)
        #print(ttasks)
        pmap = {}
        for tt in ttasks:
            already_planned = False
            if self.planned_label_id in tt.labels:
                #print("already planned: ", tt.content)
                already_planned = True
            elif tt.date_string:
                #print("manually planned, skip: ", tt.content)
                #self.manual_planned.append(tt)
                continue
            t = self.PyTaskAdapter(tt)
            #print(t)
            if already_planned:
                self.already_planned.append(t)

            if not pmap.has_key(tt.project):
                tp = tt.project
                p = Project()
                p.id = tp.id
                p.name = tp.name
                p._data = tp

                m = re.match(r"(\d+)\-(.*)", p.name)
                if m:
                    p.name = m.group(2)
                    p.priority = int(m.group(1))
                p.tasks.append(t)
                pmap[tt.project] = p
            else:
                p = pmap[tt.project]
                p.tasks.append(t)

        projects = []
        for k, v in pmap.iteritems():
            projects.append(v)

        return projects

    def get_projects_old(self):
        self.get_ttasks()
        projects = self.fc.get("projects")
        if projects is None:
            dlog("projects MISS")
            #projects = self.user.get_projects()
            projects = self.get_projects()
            self.fc.set("projects", projects)
        else:
            dlog("projects HIT")

        res = []
        for tp in projects:
            p = Project()
            p.id = tp.id
            p.name = tp.name
            p._data = tp

            m = re.match(r"(\d+)\-(.*)", p.name)
            if m:
                p.name = m.group(2)
                p.priority = int(m.group(1))

            key = "ttasks-" + p.name
            ttasks = self.fc.get(key)
            if ttasks is None:
                dlog(key + " MISS")
                ttasks = tp.get_tasks()
                self.fc.set(key, ttasks)

            ttasks = sorted(ttasks, key=lambda x:x.item_order)
            for tt in ttasks:
                already_planned = False
                if self.planned_label_id in tt.labels:
                    #print("already planned: ", tt.content)
                    already_planned = True
                elif tt.date_string:
                    #print("manually planned, skip: ", tt.content)
                    #self.manual_planned.append(tt)
                    continue
                t = self.PyTaskAdapter(tt)
                p.tasks.append(t)
                if already_planned:
                    self.already_planned.append(t)

            res.append(p)

        return res

    def clean_up(self):
        for t in self.already_planned:
            #t = app.already_planned[k]
            #print("clean up "+ t.name)
            tt = t._data
            #tt.date_string = ""
            self.update_task(t, "date_string", "", set_attr=False)
            #print("labels before")
            #print(t.labels)
            if self.planned_label_id in tt.labels:
                #tt.labels.remove(self.planned_label_id)
                #tt.labels = tt.labels[:]
                labels = tt.labels[:]
                labels.remove(self.planned_label_id)
                self.update_task(t, "labels", labels, set_attr=False)
            #print("labels after")
            #print(t.labels)
            #tt.update()
            #time.sleep(0.5)

    def update_task(self, task, key, value, set_attr=True):

        if TO_UPDATE.has_key(task.id):
            info = TO_UPDATE[task.id]
        else:
            info = {}
            TO_UPDATE[task.id] = info
        info[key] = value
        info["object"] = task
        if set_attr:
            setattr(task, key, value)

    def execute_commands(self, updates):
        commands = json.dumps(updates)
        length = len(updates)
        rounds = int(math.ceil(len(commands) / 2000.0))
        n = rounds
        while n > 0:
            s = updates[0:length/rounds]
            updates = updates[length/rounds:]

            # Too large, split
            dlog("updating current batch: %d updates" % len(s))
            #pre_update = updates[:len(updates)/2]
            commands = json.dumps(s)
            print "commands:", commands
            response = todoist.API.sync(self.user.api_token, None, None, commands=commands)
            print "status:", response.status_code
            n -= 1

            #commands = json.dumps(updates[len(updates)/2:])

        #print "commands:", commands
        #response = todoist.API.sync(self.user.api_token, None, None, commands=commands)
        #print "status:", response.status_code

        #print("text:", response.text)


    def update(self):
        self.clean_up()

        updates = []
        for id, info in TO_UPDATE.iteritems():
            t = info["object"]
            update_table = {"id": t.id}
            for k, v in info.iteritems():
                if k == "object":
                    continue
                #update_table[k] = getattr(t, k)
                update_table[k] = v
            cmd = self.get_command(self.user, "item_update", update_table)
            updates.append(cmd)
        #print(updates)
        TO_UPDATE.clear()

        self.execute_commands(updates)


    def update_project(self, project):
        p = project
        i = 0
        updates = []
        if len(p.tasks) < 1:
            return
        for t in p.tasks:
            # Get pytodoist task
            tt = t._data
            cmd = self.get_command(self.user, "item_update", {"id": t.id, "item_order": i})
            i += 1
            updates.append(cmd)
        #break
        self.execute_commands(updates)

    def update_projects(self, projects):
        for p in projects:
            self.update_project(p)

    def get_completed_tasks(self):
        res = []
        tasks = self.fc.get("completed_tasks")
        if tasks is None:
            dlog("completed tasks MISS")
            tasks = self.user.get_completed_tasks()
            self.fc.set("completed_tasks", tasks)
        else:
            dlog("completed tasks HIT")

        for t in tasks:
            res.append(self.PyTaskAdapter(t))

        res = sorted(res, key=lambda x: x.ts_done, reverse=True)
        self.completed_tasks = res

        return res

    def num_tasks_completed_today(self):
        now = datetime.utcnow()
        n = 0

        if not self.completed_tasks:
            self.get_completed_tasks()

        for item in self.completed_tasks:
            #print(item)
            if same_date(now, item.ts_done):
                n = n + 1

        return n

    def mark_as_planned(self, task):
        #print("mark as planned", task)
        tt = task._data
        if len(tt.labels) == 0:
            #tt.labels = [self.planned_label_id]
            self.update_task(tt, "labels", [self.planned_label_id], set_attr=False)
        else:
            if self.planned_label_id not in tt.labels:
                #tt.labels = tt.labels[:]
                #tt.labels.append(self.planned_label_id)
                labels = tt.labels[:]
                labels.append(self.planned_label_id)
                self.update_task(tt, "labels", labels)

        #print "labels: ", tt.labels
        #tt.update()

        if task in self.already_planned:
            self.already_planned.remove(task)

    def get_stats(self):
        ttasks = self.get_ttasks()
        return "Total number of tasks: %d" % len(ttasks)
