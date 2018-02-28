import functools
import logging
import os
import subprocess
import sys
import threading
import time
from threading import _DummyThread

log = logging.getLogger(__name__)


def retries(logger, tries=3, quiet=True):
    def inner(f):
        @functools.wraps(f)
        def inner_args(*args, **kwargs):
            for i in range(tries):
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    logger.warn("failed try #%s running function %s. args: %s exception: %s"
                                % (str(i + 1), f.func_name, str(args), unicode(e)), exc_info=True)
                    time.sleep(2 * i)
            if quiet:
                return
            raise

        return inner_args

    return inner


def exception_handler(log, quiet=True, message=None):
    def f_exception_handler(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log.exception("%s. Error: %s. Args: %s. Kwargs: %s" % (message, str(e), args, kwargs))
                if not quiet:
                    raise

        return wrapper

    return f_exception_handler


def get_top_relative_path(filepath):
    return os.path.relpath(filepath, os.getcwd())


def get_repo_url():
    raw_url = ""
    try:
        raw_url = subprocess.Popen(['git', 'config', '--get', 'remote.origin.url'], stdout=subprocess.PIPE).communicate()[0].replace("\n", "")
    except Exception as e:
        log.warning("Failed Getting Repo URL. Error: %s" % str(e))
    return raw_url


def get_commit_history():
    commits = []
    try:
        commits = subprocess.Popen(['git', 'log', '--format=%H', '-n', '100'], stdout=subprocess.PIPE).communicate()[0].split("\n")
        commits = commits[:-1]
    except Exception as e:
        log.warning("Failed Getting Commit History. Error: %s" % str(e))
    return commits


def trace(f, trace_function):
    @functools.wraps(f)
    def inner_trace(*args, **kwargs):
        value = f(*args, **kwargs)
        if type(value) == _DummyThread:
            sys.settrace(trace_function)
            threading.settrace(trace_function)
        return value
    return inner_trace
