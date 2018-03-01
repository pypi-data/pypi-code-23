#!/usr/bin/env python2.7

'''
For more information on daemons in python, see:

* http://pypi.python.org/pypi/python-daemon
* http://www.python.org/dev/peps/pep-3143/
* http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66012
* http://en.wikipedia.org/wiki/Daemon_(computing)

Here are some similar implementations:

* http://pypi.python.org/pypi/zdaemon/2.0.4
* https://github.com/indexzero/forever

This module has two separate uses cases:

* running a command as a daemon process
* forking the current process as a daemon.

Daemonizing a command allows one to start, stop, and restart a non-daemon
command as a daemon process.  This requires specifying a pid file which is used
to interact with the process.

Usage examples:

    daemoncmd start --pidfile /tmp/daemon.pid \
            --stdout /tmp/daemon.log --stderr /tmp/daemon.log sleep 100
    daemoncmd restart --pidfile /tmp/daemon.pid \
            --stdout /tmp/daemon.log --stderr /tmp/daemon.log sleep 100
    daemoncmd status --pidfile /tmp/daemon.pid
    daemoncmd stop --pidfile /tmp/daemon.pid

Another use case is forking the current process into a daemon.  According
to pep 3143, forking as a daemon might be done by the standard library some
day.

Usage example:

    import daemoncmd
    import mytask

    daemoncmd.daemonize()
    mytask.doit()

Or from the command line:

    python -c 'import daemoncmd, mytask; daemoncmd.daemonize(); mytask.doit()'

Other usage notes:

* The command should not daemonize itself, since that is what this script does
  and it would make the pid in the pidfile incorrect.
* The command should be refer to the absolute path of the executable, since
  daemonization sets the cwd to '/'.  More generally, do not assume what the
  cwd is.
* If daemoncmd is run by monit, etc., PATH and other env vars might be
  restricted for security reasons.
* daemoncmd does not try to run the daemon as a particular uid.  That would
  be handled by a process manager like monit, launchd, init, god, etc.
* When running under monit, etc., pass environment variables to the command
  like so:

    FOO=testing daemoncmd start --pidfile /tmp/daemon.pid \
            --stdout /tmp/daemon.log printenv FOO
'''

import sys
import os
import signal
import errno
import time

def start(serve, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
    '''
    Start a new daemon, saving its pid to pidfile.
    Do not start the daemon if the pidfile exists and the pid in it is running.
    '''
    # use absolute path, since daemonize() changes cwd
    pidfile = os.path.abspath(pidfile)
    pid = getpid(pidfile)

    # start process pidfile does not have pid or the pid is not a running
    # process.
    if pid and running(pid):
        msg = "Start aborted since the process(pid=%s) is running\n" % pid
        sys.stderr.write(msg)
        sys.exit(1)
    sys.stdout.write('Starting the process\n')
    # daemonize the process here
    daemonize(stdin, stdout, stderr)
    # save pid to a file
    setpid(os.getpid(), pidfile)
    # do what you want here
    serve()


def stop(pidfile):
    '''
    pidfile: a file containing a process id.
    stop the pid in pidfile if pidfile contains a pid and it is running.
    '''
    # use absolute path, since daemonize() changes cwd
    pidfile = os.path.abspath(pidfile)
    pid = getpid(pidfile)
    # stop process (if it exists)
    if not pid:
        sys.stderr.write("Couldn't stop because the process is not running or pid file '%s' is error\n" % pidfile)
    elif not running(pid):
        sys.stderr.write("Warning: the process(pid=%s) isn't running\n" % pid)
    else:
        sys.stdout.write('Stopping the process. pid=%s\n' % pid)
        try:
            os.kill(pid, signal.SIGTERM)
            # a pause, so daemon will have a chance to stop before it gets restarted.
            time.sleep(1)
        except OSError as e:
            sys.stderr.write('Failed to terminate pid "%s". caused by %s.\n'% (pid, str(e)))
            sys.exit(1)


def restart(serve, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
    '''
    stop the process in pidfile.  start argv as a new daemon process.  save its
    pid to pidfile.
    '''
    stop(pidfile)
    start(serve, pidfile, stdin, stdout, stderr)


def status(pidfile):
    # use absolute path, since daemonize() changes cwd
    pidfile = os.path.abspath(pidfile)
    pid = getpid(pidfile)
    if pid and running(pid):
        sys.stdout.write('process running with pid=%s\n' % pid)
    else:
        sys.stdout.write('process stopped\n')


def daemonize(stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
    '''
    stdin, stdout, stderr: filename that will be opened and used to replace the
    standard file descriptors is sys.stdin, sys.stdout, sys.stderr.  Default to
    /dev/null.  Note that stderr is opened unbuffered, so if it shares a file
    with stdout then interleaved output may not appear in the order that you
    expect.

    Turn current process into a daemon.
    returns: nothing in particular.
    '''

    # use absolute path, since daemonize() changes cwd
    stdin = os.path.abspath(stdin)
    stdout = os.path.abspath(stdout)
    stderr = os.path.abspath(stderr)

    # Do first fork
    try:
        pid = os.fork()
    except OSError as e:
        sys.stderr.write("fork #1 failed: (%d) %s\n"%(e.errno, e.strerror))
        sys.exit(1)
    if pid > 0:
        sys.exit(0) # exit parent

    # Decouple from parent environment.
    os.chdir("/")
    os.umask(0)
    os.setsid()

    # Do second fork.
    try:
        pid = os.fork()
    except OSError as e:
        sys.stderr.write("fork #2 failed: (%d) %s\n"%(e.errno, e.strerror))
        sys.exit(1)
    if pid > 0:
        sys.exit(0) # exit parent

    # Now I am a daemon!

    # Redirect standard file descriptors. First open the new files, perform
    # hack if necessary, flush any existing output, and dup new files to std
    # streams.
    si = open(stdin, 'r')
    so = open(stdout, 'w')
    se = open(stderr, 'w')

    # hack and bug: when sys.stdin.close() has already been called,
    # os.dup2 throws an exception: ValueError: I/O operation on closed file
    # This hack attempts to detect whether any of the std streams
    # have been closed and if so opens them to a dummy value which
    # will get closed by os.dup2, which I like better than
    # an exception being thrown.
    if sys.stdin.closed: sys.stdin = open('/dev/null', 'r')
    if sys.stdout.closed: sys.stdout = open('/dev/null', 'w')
    if sys.stderr.closed: sys.stderr = open('/dev/null', 'w')

    sys.stdout.flush()
    sys.stderr.flush()

    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())


def getpid(pidfile):
    '''
    read pid from pidfile
    return: pid
    '''
    pid = None
    if os.path.isfile(pidfile):
        with open(pidfile) as fh:
            try:
                pid = int(fh.read().strip())
            except ValueError:
                pass
    return pid


def setpid(pid, pidfile):
    '''
    save pid to pidfile
    '''
    with open(pidfile, 'w') as fh:
        fh.write('{0}\n'.format(pid))


def running(pid):
    """
    pid: a process id
    Return: False if the pid is None or if the pid does not match a
    currently-running process.
    Derived from code in http://pypi.python.org/pypi/python-daemon/ runner.py
    """
    if pid is None:
        return False
    try:
        os.kill(pid, signal.SIG_DFL)
    except OSError as exc:
        if exc.errno == errno.ESRCH:
            # The specified PID does not exist
            return False
    return True

