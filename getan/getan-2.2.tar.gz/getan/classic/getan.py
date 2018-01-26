#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# getan
# -----
# (c) 2008 by Sascha L. Teichmann <sascha.teichmann@intevation.de>
#
# A python worklog-alike to log what you have 'getan' (done).
#
# This is Free Software licensed under the terms of GPLv3 or later.
# For details see LICENSE coming with the source of 'getan'.
#
import sys
import re
import curses
import curses.ascii
import traceback
import signal

from datetime import datetime, timedelta, tzinfo

from pysqlite2 import dbapi2 as db

PAUSED      = 0
RUNNING     = 1
PRE_EXIT    = 2
PAUSED_ESC  = 3
RUNNING_ESC = 4

SPACE = re.compile("[\\t ]+")

DEFAULT_DATABASE = "time.db"

LOAD_ACTIVE_PROJECTS = '''
SELECT id, key, description, total
FROM projects LEFT JOIN
(SELECT 
    project_id, 
    sum(strftime('%s', stop_time) - strftime('%s', start_time)) AS total
    FROM entries 
    GROUP BY project_id) ON project_id = id
    WHERE active
'''

WRITE_LOG = '''
INSERT INTO entries (project_id, start_time, stop_time, description)
VALUES(:project_id, :start_time, :stop_time, :description)
'''

CREATE_PROJECT = '''
INSERT INTO projects (key, description) VALUES (:key, :description)
'''

LAST_PROJECT_ID = '''
SELECT last_insert_rowid()
'''

RENAME_PROJECT = '''
UPDATE projects set key = :key, description = :description WHERE id = :id
'''

ASSIGN_LOGS = '''
UPDATE entries SET project_id = :new_id WHERE project_id = :old_id
'''

DELETE_PROJECT = '''
DELETE FROM projects WHERE id = :id
'''

# XXX: This is not very efficent!
LAST_ENTRY = '''
SELECT id, strftime('%s', start_time), strftime('%s', stop_time) FROM entries
WHERE project_id = :project_id
ORDER by strftime('%s', stop_time) DESC LIMIT 1
'''

DELETE_ENTRY = '''
DELETE FROM entries WHERE id = :id
'''

UPDATE_STOP_TIME = '''
UPDATE entries SET stop_time = :stop_time WHERE id = :id
'''

worklog = None
stdscr  = None

orig_vis = None

def cursor_visible(flag):
    global orig_vis
    try:
        old = curses.curs_set(flag)
        if orig_vis is None: orig_vis = old
        return old
    except:
        pass
    return 1

def restore_cursor():
    global orig_vis
    if not orig_vis is None:
        curses.curs_set(orig_vis)

def render_header(ofs=0):
    global stdscr
    stdscr.attron(curses.A_BOLD)
    stdscr.addstr(ofs,   5, "getan v0.1")
    stdscr.addstr(ofs+1, 3, "--------------")
    stdscr.attroff(curses.A_BOLD)
    return ofs + 2

def render_quit(ofs=0):
    global stdscr
    stdscr.addstr(ofs + 2, 3, "Press DEL once more to quit")
    return ofs + 3

def tolerantClose(cur):
    if cur:
        try: cur.close()
        except: pass

def ifNull(v, d):
    if v is None: return d
    return v

def human_time(delta):
    seconds = delta.seconds
    s = seconds % 60
    if delta.microseconds >= 500000: s += 1
    seconds /= 60
    m = seconds % 60
    seconds /= 60
    out = "%02d:%02d:%02d" % (seconds, m, s)
    if delta.days:
        out = "%dd %s" % (delta.days, out)
    return out

FACTORS = {
    's':        1,
    'm':       60,
    'h'   : 60*60,
    'd': 24*60*60}

def human_seconds(timespec):
    """Translate human input to seconds, default factor is minutes"""
    total = 0
    for v in timespec.split(':'):
        factor = FACTORS.get(v[-1])
        if factor: v = v[:-1]
        else:      factor = 60
        total += int(v) * factor
    return total

ESC_MAP = {
    curses.KEY_F1 : ord('1'),
    curses.KEY_F2 : ord('2'),
    curses.KEY_F3 : ord('3'),
    curses.KEY_F4 : ord('4'),
    curses.KEY_F5 : ord('5'),
    curses.KEY_F6 : ord('6'),
    curses.KEY_F7 : ord('7'),
    curses.KEY_F8 : ord('8'),
    curses.KEY_F9 : ord('9'),
    curses.KEY_F10: ord('0'),
}

ZERO = timedelta(0)

class UTC(tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO    

class Project:

    def __init__(self, id = None, key = None, desc = None, total = 0):
        self.id         = id
        self.key        = key
        self.desc       = desc
        self.total      = timedelta(seconds = ifNull(total, 0))
        self.start_time = None

    def checkExistence(self, cur):
        if self.id is None:
            cur.execute(CREATE_PROJECT, {
                'key'        : self.key,
                'description': self.desc})
            cur.execute(LAST_PROJECT_ID)
            row = cur.fetchone()
            cur.connection.commit()
            self.id = row[0]

    def writeLog(self, cur, description = None):
        if self.start_time is None: return
        self.checkExistence(cur)
        now = datetime.now()
        cur.execute(WRITE_LOG, {
            'project_id' : self.id,
            'start_time' : self.start_time,
            'stop_time'  : now,
            'description': description})
        self.total += now-self.start_time
        return now

    def getId(self, cur):
        self.checkExistence(cur)
        return self.id

    def rename(self, cur, key, desc):
        self.key  = key
        self.desc = desc
        self.checkExistence(cur)
        cur.execute(RENAME_PROJECT, {
            'key'        : key,
            'description': desc,
            'id'         : self.id })
        cur.connection.commit()

    def assignLogs(self, cur, anon):
        self.total += anon.total
        anon.total = timedelta(seconds=0)
        old_id = anon.getId(cur)
        new_id = self.getId(cur)
        cur.execute(ASSIGN_LOGS, {
            'new_id': new_id,
            'old_id': old_id})
        cur.connection.commit()

    def delete(self, cur):
        pid = self.getId(cur)
        cur.execute(DELETE_PROJECT, { 'id': pid })
        cur.connection.commit()

    def subtractTime(self, cur, seconds):
        subtractTimeed, zero = timedelta(), timedelta()
        pid = {'project_id': self.getId(cur)}
        utc = UTC()
        while seconds > zero:
            cur.execute(LAST_ENTRY, pid)
            row = cur.fetchone()
            if row is None: break
            # TODO: evaluate egenix-mx
            start_time = datetime.fromtimestamp(float(row[1]), utc)
            stop_time  = datetime.fromtimestamp(float(row[2]), utc)
            runtime = stop_time - start_time
            if runtime <= seconds:
                cur.execute(DELETE_ENTRY, { 'id': row[0] })
                cur.connection.commit()
                seconds -= runtime
                subtractTimeed += runtime
            else:
                stop_time -=  seconds
                cur.execute(UPDATE_STOP_TIME, {
                    'id': row[0],
                    'stop_time': stop_time})
                cur.connection.commit()
                subtractTimeed += seconds
                break

        self.total -= subtractTimeed
        return subtractTimeed

    def addTime(self, cur, seconds, description):
        now = datetime.now()
        cur.execute(WRITE_LOG, {
            'project_id' : self.getId(cur),
            'start_time' : now - seconds,
            'stop_time'  : now,
            'description': description
        })
        cur.connection.commit()
        self.total += seconds

def build_tree(project, depth):
    if len(project.key) == depth+1:
        return ProjectNode(project, project.key[depth])
    node = ProjectNode(None, project.key[depth])
    node.children.append(build_tree(project, depth+1))
    return node

class ProjectNode:

    def __init__(self, project = None, key = None):
        self.children = []
        self.project  = project
        self.key      = key

    def insertProject(self, project, depth = 0):

        if not project.key: # anonym -> end
            node = ProjectNode(project)
            self.children.append(node)
            return

        for i, child in enumerate(self.children):
            if not child.key: # before anonym projects
                self.children.insert(i, build_tree(project, depth))
                return
            if child.key == project.key[depth]:
                child.insertProject(project, depth+1)
                return
        self.children.append(build_tree(project, depth))

    def removeProject(self, project):

        if self.isLeaf(): return
        stack = [self]
        while stack:
            parent = stack.pop()
            for child in parent.children:
                if not child.isLeaf():
                    stack.append(child)
                    continue
                if child.project == project:
                    parent.children.remove(child)
                    return

    def isLeaf(self):
        return not self.project is None

    def findProject(self, key):
        l, lower = key.lower(), None
        for child in self.children:
            if child.key == key:
                return child
            if child.key and child.key.lower() == l:
                lower = child
        return lower

    def dump(self, depth = 0):
        out = []
        indent = "  " * depth
        out.append("%skey: %s" % (indent, self.key))
        if self.project:
            out.append("%sdescription: %s" % (indent, self.project.desc))
        for child in self.children:
            out.append(child.dump(depth+1))
        return "\n".join(out)

class Worklog:

    def __init__(self, database):
        self.initDB(database)
        self.projects        = []
        self.tree            = ProjectNode()
        self.state           = PAUSED
        self.current_project = None
        self.selection       = self.tree
        self.stack           = []
        self.loadProjects()

    def initDB(self, database):
        self.con = db.connect(database)

    def loadProjects(self):
        cur = None
        try:
            cur = self.con.cursor()
            cur.execute(LOAD_ACTIVE_PROJECTS)
            while True:
                row = cur.fetchone()
                if not row: break
                project = Project(*row)
                self.projects.append(project)
                self.tree.insertProject(project)
        finally:
            tolerantClose(cur)

    def shutdown(self):
        self.con.close()

    def fetchStack(self):
        cut = ''.join([chr(i) for i in self.stack])
        self.stack = []
        return cut

    def findProject(self, key):
        key_lower = key.lower()
        lower = None

        for p in self.projects:
            if p.key == key:
                return p
            if p.key and p.key.lower() == key_lower:
                lower = p

        return lower

    def findAnonymProject(self, num):
        count = 0
        for p in self.projects:
            if p.key is None:
                if count == num:
                    return p
                count += 1
        return None

    def renameAnonymProject(self, num, key, description):
        project = self.findAnonymProject(num)
        if project:
            cur = None
            try:
                cur = self.con.cursor()
                project.rename(cur, key, description)
            finally:
                tolerantClose(cur)
            self.tree.removeProject(project)
            self.tree.insertProject(project)
                    
    def assignLogs(self, num, key):
        anon = self.findAnonymProject(num)
        if anon is None: return
        project = self.findProject(key)
        if project is None: return
        cur = None
        try:
            cur = self.con.cursor()
            project.assignLogs(cur, anon)
            self.projects.remove(anon)
            anon.delete(cur)
        finally:
            tolerantClose(cur)

    def addTime(self, key, seconds, description = None):
        project = self.findProject(key)
        if project is None: return
        cur = None
        try:
            cur = self.con.cursor()
            project.addTime(cur, seconds, description)
        finally:
            tolerantClose(cur)

    def subtractTime(self, key, seconds):
        project = self.findProject(key)
        if project is None: return
        cur = None
        try:
            cur = self.con.cursor()
            project.subtractTime(cur, seconds)
        finally:
            tolerantClose(cur)

    def isRunning(self):
        return self.state in (RUNNING, RUNNING_ESC)

    def totalTime(self):
        sum = timedelta()
        for p in self.projects:
            sum += p.total
        return sum

    def render(self, ofs=0):
        ofs = render_header(ofs)
        ml = max([len(p.desc and p.desc or "unknown") for p in self.projects])
        unknown = 0

        if self.current_project and self.current_project.start_time:
            current_delta      = datetime.now() - self.current_project.start_time 
            current_time_str   = "%s " % human_time(current_delta)
            current_time_space = " " * len(current_time_str)
        else:
            current_delta      = timedelta()
            current_time_str   = ""
            current_time_space = ""

        for project in self.projects:
            is_current = project == self.current_project
            pref = is_current and " -> " or "    "
            if project.key is None:
                key = "^%d" % unknown
                unknown += 1
            else:
                key = " %s" % project.key
            desc = project.desc is None and "unknown" or project.desc
            stdscr.attron(curses.A_BOLD)
            stdscr.addstr(ofs, 0, "%s%s" % (pref, key))
            stdscr.attroff(curses.A_BOLD)
            stdscr.addstr(" %s" % desc)

            diff = ml - len(desc) + 1
            stdscr.addstr(" " * diff)
            if is_current: stdscr.attron(curses.A_UNDERLINE)

            if is_current:
                stdscr.addstr("%s(%s)" % (
                    current_time_str,
                    human_time(project.total + current_delta)))
            else:
                stdscr.addstr("%s(%s)" % (
                    current_time_space,
                    human_time(project.total)))

            if is_current: stdscr.attroff(curses.A_UNDERLINE)
            ofs += 1

        total_str   = "(%s)" % human_time(self.totalTime() + current_delta) 
        total_x_pos = ml + 8 + len(current_time_space)

        stdscr.addstr(ofs, total_x_pos, "=" * len(total_str))
        ofs += 1
        stdscr.addstr(ofs, total_x_pos, total_str)
        ofs += 1

        return ofs

    def writeLog(self, description = None):
        if self.current_project is None:
            return datetime.now()
        cur = None
        try:
            cur = self.con.cursor()
            now = self.current_project.writeLog(cur, description)
            self.con.commit()
            return now
        finally:
            tolerantClose(cur)

    def pausedState(self, c):
        c2 = ESC_MAP.get(c)
        if c2:
            self.pausedEscapeState(c2)
            return

        global stdscr
        if c in (curses.KEY_DC, curses.KEY_BACKSPACE):
            stdscr.erase()
            ofs = render_quit(self.render())
            stdscr.refresh()
            self.state = PRE_EXIT

        elif c == curses.ascii.ESC:
            self.state = PAUSED_ESC

        elif curses.ascii.isascii(c):
            if c == ord('-'):
                self.selection = self.tree
                stdscr.erase()
                ofs = self.render()
                old_cur = cursor_visible(1)
                curses.echo()
                stdscr.addstr(ofs + 1, 3, "<key> <minutes>: ")
                key = stdscr.getstr()
                curses.noecho()
                cursor_visible(old_cur)
                key = key.strip()
                if key:
                    parts = SPACE.split(key, 1)
                    if len(parts) > 1:
                        key, timespec = parts[0], parts[1]
                        try:
                            seconds = human_seconds(timespec)
                            if seconds > 0:
                                seconds = timedelta(seconds=seconds)
                                self.subtractTime(key, seconds)
                        except ValueError:
                            pass
                stdscr.erase()
                self.render()
                stdscr.refresh()

            elif c == ord('+'):
                self.selection = self.tree
                stdscr.erase()
                ofs = self.render()
                old_cur = cursor_visible(1)
                curses.echo()
                stdscr.addstr(ofs + 1, 3, "<key> <minutes> [<description>]: ")
                key = stdscr.getstr()
                curses.noecho()
                cursor_visible(old_cur)
                key = key.strip()
                if key:
                    parts = SPACE.split(key, 2)
                    if len(parts) > 1:
                        key, timespec = parts[0], parts[1]
                        if len(parts) > 2: desc = parts[2]
                        else:              desc = None
                        try:
                            seconds = human_seconds(timespec)
                            if seconds > 0:
                                seconds = timedelta(seconds=seconds)
                                self.addTime(key, seconds, desc)
                        except ValueError:
                            pass
                stdscr.erase()
                self.render()
                stdscr.refresh()

            else:
                node = self.selection.findProject(chr(c))
                if not node:
                    self.selection = self.tree
                    return
                if node.isLeaf():
                    self.selection = self.tree
                    nproject = node.project
                    self.current_project = nproject
                    nproject.start_time = datetime.now()
                    stdscr.erase()
                    ofs = self.render()
                    stdscr.refresh()
                    self.state = RUNNING
                    signal.signal(signal.SIGALRM, alarm_handler)
                    signal.alarm(1)
                else:
                    self.selection = node

    def runningState(self, c):
        global stdscr
        c2 = ESC_MAP.get(c)
        if c2:
            self.runningEscapeState(c2)
            return

        if c == curses.ascii.ESC:
            self.state = RUNNING_ESC

        elif c == curses.ascii.NL:
            signal.signal(signal.SIGALRM, signal.SIG_IGN)
            self.state = PAUSED
            stdscr.erase()
            ofs = self.render()
            old_cur = cursor_visible(1)
            curses.echo()
            stdscr.addstr(ofs + 1, 3, "Description: ")
            description = stdscr.getstr()
            curses.noecho()
            cursor_visible(old_cur)
            self.writeLog(description)
            self.current_project = None
            stdscr.erase()
            ofs = self.render()
            stdscr.refresh()
            signal.signal(signal.SIGALRM, alarm_handler)
            signal.alarm(1)
        elif c == ord('+'):
            signal.signal(signal.SIGALRM, signal.SIG_IGN)
            stdscr.erase()
            ofs = self.render()
            if self.stack:
                timespec = self.fetchStack()
            else:
                old_cur = cursor_visible(1)
                curses.echo()
                stdscr.addstr(ofs + 1, 3, "Enter time to add: ")
                timespec = stdscr.getstr()
                curses.noecho()
                cursor_visible(old_cur)
                stdscr.erase()
                ofs = self.render()
            try:
                seconds = human_seconds(timespec)
                if seconds > 0:
                    seconds = timedelta(seconds=seconds)
                    self.current_project.start_time -= seconds
                    stdscr.addstr(ofs + 1, 3, "added %s" % human_time(seconds))
            except (ValueError, IndexError):
                pass
            stdscr.refresh()
            signal.signal(signal.SIGALRM, alarm_handler)
            signal.alarm(1)
        elif c == ord('-'):
            signal.signal(signal.SIGALRM, signal.SIG_IGN)
            stdscr.erase()
            ofs = self.render()
            if self.stack:
                timespec = self.fetchStack()
            else:
                old_cur = cursor_visible(1)
                curses.echo()
                stdscr.addstr(ofs + 1, 3, "Enter time to subtract: ")
                timespec = stdscr.getstr()
                curses.noecho()
                cursor_visible(old_cur)
                stdscr.erase()
                ofs = self.render()
            try:
                seconds = human_seconds(timespec)
                if seconds > 0:
                    now = datetime.now()
                    seconds = timedelta(seconds=seconds)
                    self.current_project.start_time += seconds
                    stdscr.addstr(ofs + 1, 3, "subtracted %s" % human_time(seconds))
                    if self.current_project.start_time > now:
                        seconds = self.current_project.start_time - now
                        self.current_project.start_time = now
                        cur = None
                        try:
                            cur = self.con.cursor()
                            self.current_project.subtractTime(cur, seconds)
                        finally:
                            tolerantClose(cur)
            except (ValueError, IndexError):
                pass
            stdscr.refresh()
            signal.signal(signal.SIGALRM, alarm_handler)
            signal.alarm(1)
        elif self.stack or curses.ascii.isdigit(c):
            self.stack.append(c)
        elif curses.ascii.isascii(c):
            project_node = self.selection.findProject(chr(c))
            if project_node is None:
                self.selection = self.tree
                return

            if project_node.isLeaf():
                self.selection = self.tree
                nproject = project_node.project
                if nproject == self.current_project:
                    return
                nproject.start_time = self.writeLog()
                self.current_project = nproject
                stdscr.erase()
                ofs = self.render()
                stdscr.refresh()
            else:
                self.selection = project_node

    def pausedEscapeState(self, c):
        global stdscr
        if curses.ascii.isdigit(c):
            pnum = c - ord('0')
            nproject = self.findAnonymProject(pnum)
            if nproject is None:
                nproject = Project()
                self.projects.append(nproject)

            nproject.start_time = self.writeLog()
            self.current_project = nproject
            self.state = RUNNING
            stdscr.erase()
            ofs = self.render()
            stdscr.refresh()
            signal.signal(signal.SIGALRM, alarm_handler)
            signal.alarm(1)
        elif curses.ascii.isalpha(c):
            if c == ord('n'):
                stdscr.erase()
                ofs = self.render()
                old_cur = cursor_visible(1)
                curses.echo()
                stdscr.addstr(ofs + 1, 3, "<num> <key> <description>: ")
                stdscr.refresh()
                description = stdscr.getstr()
                curses.noecho()
                cursor_visible(old_cur)

                description = description.strip()
                if description:
                    num, key, description = SPACE.split(description, 2)
                    try:
                        num = int(num)
                        self.renameAnonymProject(num, key, description)
                    except ValueError:
                        pass

                stdscr.erase()
                ofs = self.render()
                stdscr.refresh()
                self.state = PAUSED

            elif c == ord('a'):
                stdscr.erase()
                ofs = self.render()
                old_cur = cursor_visible(1)
                curses.echo()
                stdscr.addstr(ofs + 1, 3, "<num> <key>: ")
                stdscr.refresh()
                key = stdscr.getstr()
                curses.noecho()
                cursor_visible(old_cur)

                key = key.strip()
                if key:
                    num, key = SPACE.split(key, 1)
                    try:
                        num = int(num)
                        self.assignLogs(num, key)
                    except ValueError:
                        pass

                stdscr.erase()
                ofs = self.render()
                stdscr.refresh()
                self.state = PAUSED
            else:
                self.state = PAUSED
        else:
            self.state = PAUSED

    def runningEscapeState(self, c):
        global stdscr
        if curses.ascii.isdigit(c):
            signal.signal(signal.SIGALRM, signal.SIG_IGN)
            pnum = c - ord('0')
            nproject = self.findAnonymProject(pnum)
            if nproject is None:
                nproject = Project()
                self.projects.append(nproject)

            nproject.start_time = self.writeLog()
            self.current_project = nproject
            self.state = RUNNING
            stdscr.erase()
            self.render()
            stdscr.refresh()
            signal.signal(signal.SIGALRM, alarm_handler)
            signal.alarm(1)
        else:
            self.state = RUNNING
        

    def run(self):
        global stdscr

        stdscr.erase()
        self.render()
        stdscr.refresh()

        while True:
            c = stdscr.getch()
            if c == -1: continue

            if self.state == PAUSED:
                self.pausedState(c)

            elif self.state == RUNNING:
                self.runningState(c)

            elif self.state == PAUSED_ESC:
                self.pausedEscapeState(c)

            elif self.state == RUNNING_ESC:
                self.runningEscapeState(c)

            elif self.state == PRE_EXIT:
                if c in (curses.KEY_DC, curses.KEY_BACKSPACE):
                    break
                else:
                    stdscr.erase()
                    self.render()
                    stdscr.refresh()
                    self.state = PAUSED

def alarm_handler(flag, frame):
    global worklog
    global stdscr

    stdscr.erase()
    worklog.render()
    stdscr.refresh()
    if worklog.isRunning():
        signal.alarm(1)

def exit_handler(flag, frame):
    exit_code = 0
    global worklog
    try:
        worklog.shutdown()
    except:
        traceback.print_exc(file=sys.stderr)
        exit_code = 1

    restore_cursor()
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()
    sys.exit(exit_code)

def main():

    database = len(sys.argv) < 2 and DEFAULT_DATABASE or sys.argv[1]
    # TODO: create database file if it does not exist.

    global worklog
    try:
        worklog = Worklog(database)
    except:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

    global stdscr
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(1)
    cursor_visible(0)

    signal.signal(signal.SIGHUP,  exit_handler)
    signal.signal(signal.SIGINT,  exit_handler)
    signal.signal(signal.SIGQUIT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)
    
    try:
        try:
            worklog.run()
        except:
            traceback.print_exc(file=sys.stderr)
    finally:
        exit_handler(0, None)

if __name__ == '__main__':
    main()

# vim:set ts=4 sw=4 si et sta sts=4 fenc=utf8:
