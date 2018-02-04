import argparse
import atexit
import errno
import logging
import os
import signal
import sys
from time import sleep
from traceback import print_exc

from minipyp.minipyp import MiniPyP, Request, Server, Handler

level = logging.INFO


def start(args, config):
    if args.attached:
        MiniPyP(config).start()
    elif sys.platform == 'win32':
        print('minipyp: error: daemons are not supported on Windows, please use --attached (-a)')
        sys.exit(1)
    else:
        pid = get_pid()
        if pid is not None and pid != -1:
            print('minipyp: error: server is already running')
            sys.exit(1)
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError:
            print('minipyp: error: failed to fork (first time)')
            print_exc()
            sys.exit(1)
        os.chdir('.')
        os.setsid()
        os.umask(0o22)
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError:
            print('minipyp: error: failed to fork (second time)')
            print_exc()
            sys.exit(1)
        if sys.platform != 'darwin':
            sys.stdout.flush()
            sys.stderr.flush()
            stdin = open(os.devnull, 'r')
            stdout = open(os.devnull, 'a+')
            os.dup2(stdin.fileno(), sys.stdin.fileno())
            os.dup2(stdout.fileno(), sys.stdout.fileno())
            os.dup2(stdout.fileno(), sys.stderr.fileno())
        with open('/var/run/minipyp.pid', 'w+') as file:
            file.write(str(os.getpid()) + '\n')
        atexit.register(cleanup)
        server = MiniPyP(config)
        minipyp.log.setLevel(level)
        server.start()


def stop(args):
    if sys.platform == 'win32':
        print('minipyp: error: daemons are not supported on Windows')
        sys.exit(1)
    pid = get_pid()
    if pid is None or pid == -1:
        print('minipyp: error: server is ' + ('stopped' if pid is None else 'dead'))
        if os.path.exists('/var/run/minipyp.pid'):
            os.remove('/var/run/minipyp.pid')
        return
    try:
        i = 0
        while True:
            os.kill(pid, signal.SIGTERM)
            sleep(0.1)
            i = i + 1
            if i % 10 == 0:
                if hasattr(signal, 'SIGHUP'):
                    os.kill(pid, signal.SIGHUP)
                else:
                    print('minipyp: error: SIGHUP is not supported on this system')
                    sys.exit(1)
    except OSError as e:
        if e.errno == errno.ESRCH:
            if os.path.exists('/var/run/minipyp.pid'):
                os.remove('/var/run/minipyp.pid')
        else:
            print('minipyp: error: failed to stop server')
            print_exc()
            sys.exit(1)


def reload(args):
    if sys.platform == 'win32':
        print('minipyp: error: daemons are not supported on Windows')
        sys.exit(1)
    pid = get_pid()
    if pid is None or pid == -1:
        print('minipyp: error: server is ' + ('stopped' if pid is None else 'dead'))
        sys.exit(1)
    if hasattr(signal, 'SIGHUP'):
        try:
            os.kill(pid, signal.SIGHUP)
        except OSError as e:
            if e.errno == errno.ESRCH:
                pass
            else:
                print('minipyp: error: failed to signal reload')
                print_exc()
                sys.exit(1)
    else:
        print('minipyp: error: SIGHUP is not supported on this system')
        sys.exit(1)


def status(args):
    if sys.platform == 'win32':
        print('minipyp: error: daemons are not supported on Windows, please use --attached (-a)')
        sys.exit(1)
    pid = get_pid()
    if pid is None:
        print('minipyp: stopped')
    elif pid == -1:
        print('minipyp: dead')
    else:
        print('minipyp: running with pid ' + str(pid))


def get_pid():
    try:
        with open('/var/run/minipyp.pid', 'r') as file:
            pid = int(file.read().strip())
            if os.path.exists('/proc/' + str(pid)):
                return pid
            return -1
    except (SystemExit, IOError):
        pass
    return None


def cleanup():
    try:
        with open('/var/run/minipyp.pid', 'r') as file:
            pid = file.read().strip()
            if pid == os.getpid():
                os.remove('/var/run/minipyp.pid')
    except OSError as e:
        if e.errno == errno.ENOENT:
            pass
        else:
            print('minipyp: error: cleanup failed')
            print_exc()


def main():
    global level
    proc = argparse.ArgumentParser(prog='minipyp', description='manage a minipyp server:')
    manage = proc.add_subparsers(dest='do')
    c_start = manage.add_parser('start', help='start the server')
    c_start.add_argument('-v', '--verbose', help='show all logs', action='store_true')
    c_start.add_argument('-a', '--attached', help='run in foreground', action='store_true')
    c_start.add_argument('-c', '--config', help='use config file')
    c_stop = manage.add_parser('stop', help='stop the server')
    c_stop.add_argument('-v', '--verbose', help='show all logs', action='store_true')
    c_restart = manage.add_parser('restart', help='restart the server')
    c_restart.add_argument('-v', '--verbose', help='show all logs', action='store_true')
    c_restart.add_argument('-c', '--config', help='use config file')
    c_reload = manage.add_parser('reload', help='reload the server config')
    c_reload.add_argument('-v', '--verbose', help='show all logs', action='store_true')
    c_status = manage.add_parser('status', help='get server status')
    c_status.add_argument('-v', '--verbose', help='get more info', action='store_true')
    args = proc.parse_args()
    config = None
    if hasattr(args, 'config'):
        config = args.config
        if not config:
            if sys.platform == 'win32':
                config = os.path.join(os.getenv('APPDATA'), 'MiniPyP')
            else:
                config = os.path.join(os.sep, 'etc', 'minipyp')
            if not os.path.exists(config):
                os.makedirs(config)
            config = os.path.join(config, 'minipyp.conf')
        if not os.path.exists(config):
            with open(os.path.join(os.path.dirname(__file__), 'minipyp.conf')) as conf:
                basic_config = conf.read()
            with open(config, 'w') as conf:
                conf.write(basic_config)
    level = minipyp.log.getEffectiveLevel()
    if hasattr(args, 'verbose') and args.verbose:
        minipyp.log.setLevel(logging.DEBUG)
    if args.do == 'start':
        print('minipyp: starting server...')
        start(args, config)
    elif args.do == 'stop':
        print('minipyp: stopping server...')
        stop(args)
    elif args.do == 'restart':
        print('minipyp: restarting server...')
        stop(args)
        args.attached = False
        start(args, config)
    elif args.do == 'reload':
        print('minipyp: reloading config...')
        reload(args)
    elif args.do == 'status':
        status(args)
    else:
        proc.print_usage()
    if hasattr(args, 'verbose') and args.verbose:
        minipyp.log.setLevel(level)
