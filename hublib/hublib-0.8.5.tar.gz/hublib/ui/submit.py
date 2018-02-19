# -*- coding: utf-8 -*-
from __future__ import print_function
import ipywidgets as widgets
import sys
import re
import os
import signal
import threading
import subprocess
import select
import time
from queue import Queue


foobar='Hello WOrld!!!'

class Submit(object):
    regex = re.compile(r"=SUBMIT-PROGRESS=> aborted=(\d+) finished=(\d+) failed=(\d+) executing=(\d+) waiting=(\d+) setting_up=(\d+) setup=(\d+) %done=(\d*\.\d+|\d+) timestamp=(\d*\.\d+|\d+)")

    SIGNALS_TO_NAMES_DICT = dict((getattr(signal, n), n)
        for n in dir(signal) if n.startswith('SIG') and '_' not in n)

    def __init__(self, name='Simulate',
                 desc='Submit Simulation',
                 cb=None,
                 **kwargs):

        self.disabled = kwargs.get('disabled', False)
        self.name = name
        self.desc = desc
        self.cb = cb
        self.q = Queue()
        self.thread = 0

        print(foobar)
        
        self.but = widgets.Button(
            description=self.name,
            button_style='success'
        )

        self.but.on_click(self.but_cb)
        self.w = widgets.VBox([self.but])

    def but_cb(self, change):
        if self.but.description == self.name:
            self.but.description = 'Cancel'
            self.but.button_style = 'danger'
            if self.cb:
                self.cb(self)
            return
        if self.but.description == 'Cancel':
            self.but.description = 'Stopping'
            self.but.button_style = 'warning'
            if self.pid:
                os.killpg(self.pid, signal.SIGTERM)

    def wait(self):
        if self.thread:
            self.thread.join()
            self.thread = 0

    def start(self, cmd):
        txt = widgets.Textarea(
            layout={'width': '100%', 'height': '400px'}
        )
        self.txt = txt
        self.acc = widgets.Accordion(children=[txt])
        self.acc.set_title(0, 'Output')
        self.acc.selected_index = None
        self.w.children = (self.acc, self.but)

        if self.thread:
            # cleanup old thread
            self.thread.join()

        self.thread = threading.Thread(target=poll_thread, args=(cmd, txt, self))
        self.thread.start()
        self.pid = os.getpgid(self.q.get())

    def _ipython_display_(self):
        self.w._ipython_display_()


def poll_thread(cmd, owidget, self):
    # set the output encoding
    outenc = sys.stdout.encoding

    start_time = time.time()
    # FIXME insert status label here
    # Run Started at XXXX
    
    try:
        child = subprocess.Popen(
            cmd, bufsize=4096,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            close_fds=True,
            preexec_fn=os.setsid)
    except Exception as e:
        print(e.strerror)
        return

    self.q.put(child.pid)
    poller = select.poll()
    poller.register(child.stdout, select.POLLIN)
    poller.register(child.stderr, select.POLLIN)

    numfds = 2
    while numfds > 0:
        try:
            r = poller.poll(1)
        except select.error as err:
            print(err[1], file=sys.stderr)
            break
        for fd, flags in r:
            if flags & (select.POLLIN | select.POLLPRI):
                c = os.read(fd, 4096).decode(outenc)
                if fd == child.stderr.fileno():
                    if c.endswith('\n'):
                        c = c[:-1]
                    owidget.value += u'⇉ ' + c + u' ⇇\n'
                else:
                    # write c to output widget
                    owidget.value += c

            if flags & (select.POLLHUP | select.POLLERR):
                poller.unregister(fd)
                numfds -= 1
    
    pid, exitStatus = os.waitpid(child.pid, 0)
    elapsed_time = time.time() - start_time

    self.but.description = self.name
    self.but.button_style = 'success'  # green

    color_rect = '<svg width="4" height="20"><rect width="4" height="20" style="fill:%s"/></svg>  Last Run %s'
    colors = ["rgb(60,179,113)", "rgb(255,165,0)", "rgb(255,99,71)"]
    
    errStr = ""
    errNum = 0
    errState = "OK"
    
    if exitStatus != 0:
        if os.WIFSIGNALED(exitStatus):
            signame = Submit.SIGNALS_TO_NAMES_DICT[os.WTERMSIG(exitStatus)]
            errStr = "%s failed w/ signal %s\n" % (cmd, signame)
            errNum = 1
            errState = "Canceled"
        else:
            if os.WIFEXITED(exitStatus):
                exitStatus = os.WEXITSTATUS(exitStatus)
            errStr = "\"%s\" failed w/ exit code %d\n" % (cmd, exitStatus)
            errNum = 2
            errState = "Failed"
        owidget.value += '\n' + '='*20 + '\n' + errStr

    errState += ".  Run Time: %s" % time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
    state_str = color_rect % (colors[errNum], errState)
    status = widgets.HTML(state_str)
    self.w.children = (self.acc, status, self.but)


def rname(*args):
    return
