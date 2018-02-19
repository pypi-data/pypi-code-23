#! /usr/bin/env python
#################################################################################
#     File Name           :     tmux_schedule.py
#     Created By          :     qing
#     Creation Date       :     [2017-10-10 14:07]
#     Last Modified       :     [2017-10-10 15:08]
#     Description         :      
#################################################################################
import libtmux
import time
from schedule import schedule_bar

def worker(args):
    session_name, window_name, command, n_workers = args
    server = libtmux.Server()
    session = server.find_where({ "session_name": session_name })
    while True:
        if len(session.list_windows()) < n_workers + 1:
            break
        time.sleep(1)
    window = session.new_window(window_name=window_name)
    time.sleep(1)
    pane = window.panes[0]
    for c in command.split('\n'):
        pane.send_keys(c)
    pane.send_keys("tmux kill-window -t {:}".format(window_name))

def tmux_schedule(n_workers, session_name, commands, window_names=None):
    server = libtmux.Server()
    session = server.new_session(session_name)
    if window_names == None:
        window_names = ["job{:}".format(i+1) for i in range(len(commands))]
    args = []
    for window_name, command in zip(window_names, commands):
        args.append((session_name, window_name, command, n_workers))
    schedule_bar(worker, args, n_workers)

if __name__ == '__main__':
    commands = []
    import random
    for i in range(100):
        command = []
        command.append('pwd')
        t = random.randint(1, 7)
        command.append('sleep {:}'.format(t))
        commands.append('\n'.join(command))
    tmux_schedule(5, 'test_tmux', commands)
