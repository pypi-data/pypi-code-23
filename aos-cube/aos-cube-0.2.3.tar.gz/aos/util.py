import contextlib
import os
import sys
import shutil
import stat
import subprocess

import errno

from constant import *


# Directory navigation
@contextlib.contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(newdir)
    try:
        yield
    finally:
        os.chdir(prevdir)


def relpath(root, path):
    return path[len(root) + 1:]


def staticclass(cls):
    for k, v in cls.__dict__.items():
        if hasattr(v, '__call__') and not k.startswith('__'):
            setattr(cls, k, staticmethod(v))

    return cls


# Logging and output
def log(msg):
    sys.stdout.write(msg)
    sys.stdout.flush()


def message(msg):
    return "[AliOS-Things] %s\n" % msg


def info(msg, level=1):
    if level <= 0 or verbose:
        for line in msg.splitlines():
            log(message(line))


def action(msg):
    for line in msg.splitlines():
        log(message(line))


def warning(msg):
    for line in msg.splitlines():
        sys.stderr.write("[AliOS-Things] WARNING: %s\n" % line)
    sys.stderr.write("---\n")


def error(msg, code=-1):
    for line in msg.splitlines():
        sys.stderr.write("[AliOS-Things] ERROR: %s\n" % line)
    sys.stderr.write("---\n")
    sys.exit(code)


def progress_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor


progress_spinner = progress_cursor()


def progress():
    sys.stdout.write(progress_spinner.next())
    sys.stdout.flush()
    sys.stdout.write('\b')


# Process execution
class ProcessException(Exception):
    pass


def rmtree_readonly(directory):
    def remove_readonly(func, path, _):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    shutil.rmtree(directory, onerror=remove_readonly)


def popen(command, stdin=None, **kwargs):
    # print for debugging
    info('Exec "' + ' '.join(command) + '" in ' + os.getcwd())
    try:
        proc = subprocess.Popen(command, **kwargs)
    except OSError as e:
        if e[0] == errno.ENOENT:
            error(
                "Could not execute \"%s\".\n"
                "Please verify that it's installed and accessible from your current path by executing \"%s\".\n" % (
                command[0], command[0]), e[0])
        else:
            raise e

    if proc.wait() != 0:
        raise ProcessException(proc.returncode, command[0], ' '.join(list(command)), os.getcwd())


def pquery(command, stdin=None, **kwargs):
    if very_verbose:
        info('Query "' + ' '.join(command) + '" in ' + os.getcwd())
    try:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
    except OSError as e:
        if e[0] == errno.ENOENT:
            error(
                "Could not execute \"%s\".\n"
                "Please verify that it's installed and accessible from your current path by executing \"%s\".\n" % (
                command[0], command[0]), e[0])
        else:
            raise e

    stdout, _ = proc.communicate(stdin)

    if very_verbose:
        log(str(stdout).strip() + "\n")

    if proc.returncode != 0:
        raise ProcessException(proc.returncode, command[0], ' '.join(command), os.getcwd())

    return stdout