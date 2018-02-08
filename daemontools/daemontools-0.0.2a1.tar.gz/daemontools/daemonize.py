#!/usr/bin/env python

from __future__ import print_function
import sys, os
import pwd
import grp

''' Module to fork the current process as a daemon.
    NOTE: don't do any of this if your daemon gets started by inetd!
    inetd does all you need, including redirecting standard file descriptors;
    the chdir() and umask() steps are the only ones you may still want.

    Author: Lubos Medovarsky, lubos@medovarsky.com, 2008
    License: LGPLv3
'''

def get_user_id(user_name):
    try:
        result = pwd.getpwnam(user_name).pw_uid
    except KeyError:
        result = None
    return result

def get_user_name(uid):
    try:
        result = pwd.getpwuid(uid).pw_name
    except:
        result = None
    return result

def get_group_id(group_name):
    try:
        result = grp.getgrnam(group_name).gr_gid
    except KeyError:
        result = None
    return result

def get_group_name(gid):
    try:
        result = grp.getgrgid(gid).gr_name
    except:
        result = None
    return result

def daemonize(stdin, stdout, stderr, user = None, group = None):
    ''' Fork the current process as a daemon, redirecting standard file descriptors.'''
    # Perform first fork.
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0) # Exit first parent.
    except OSError:
        sys.stderr.write("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(1)
    # Decouple from parent environment.
    #os.chdir("/")
    os.umask(0)
    os.setsid()
    # Perform second fork.
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0) # Exit second parent.
    except OSError:
        sys.stderr.write("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(1)
    # The process is now daemonized, redirect standard file descriptors.
    for f in sys.stdout, sys.stderr:
        f.flush()
    si = open(stdin, 'r')
    so = open(stdout, 'a+')
    se = open(stderr, 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())
    if group: #drop group first,  unsuccessful otherwise
        gid = get_group_id(group)
        os.setegid(int(gid))
    if user:
        uid = get_user_id(user)
        os.seteuid(int(uid))
    return pid

def main():
    import time
    #sys.stdout.write('Daemon started with pid %d\n' % os.getpid())
    #sys.stdout.write('Daemon stdout output\n')
    #sys.stderr.write('Daemon stderr output\n')
    c = 0
    while True:
        sys.stdout.write('%d: %s\n' % (c, time.ctime()))
        sys.stdout.flush()
        c = c + 1
        time.sleep(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        log = sys.argv[1]
    else:
        log = 'daemon.log'
    print('writing to', log)
    user = 'labrecd'
    group = 'labrecd'
    #uid = get_user_id(user)
    #if not uid:
    #  exit(2)
    #gid = get_group_id(group)
    #if not gid:
    #  exit(3)
    #print 'uid', uid, 'gid', gid
    pid = daemonize('/dev/null', log, log, user, group)
    print('running with pid', os.getuid(), 'gid', os.getgid(), 'pid', os.getpid())
    main()
