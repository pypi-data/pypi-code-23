
# This script runs on the remote server and implements a REPL.  Commands are
# received, executed, and results returned.

import os, sys, traceback, functools
from io import StringIO
from os.path import isdir, exists
import importlib.util

from .protocol import encode, read_msg, hash_file


class Message:
    def __init__(self, msgdict):
        self.__dict__.update(msgdict)


class PepperInternalError(Exception):
    """
    Used for "expected" exceptions which should not print a stack trace.
    Perhaps we should use SystemExit for this?
    """
    pass


def writemsg(msg):
    header, msgbytes = encode(msg)
    sys.__stdout__.buffer.write(header)
    sys.__stdout__.buffer.write(msgbytes)
    sys.__stdout__.buffer.flush()


def main():
    """
    The REPL that reads commands, executes them, and returns results.  This
    loops until "quit" is received.
    """

    unbuffered = os.fdopen(sys.stdin.fileno(), 'rb', buffering=0)

    try:
        while 1:
            msg = read_msg(functools.partial(unbuffered.read, 50 * 1024))
            msg = Message(msg)

            if msg.msgtype == 'quit':
                break

            success = False
            try:
                func = globals().get('_handle_%s' % msg.msgtype)

                if not func:
                    raise PepperInternalError('Unhandled msgtype %r' % msg.msgtype)

                response = func(msg)
                success = True

            except PepperInternalError as ex:
                response = dict(msgtype='error', error=str(ex))
            except:
                response = dict(msgtype='error', traceback=traceback.format_exc())

            writemsg(response)
            if not success:
                break

    except:
        writemsg(dict(msgtype='error', traceback=traceback.format_exc()))


def get_lib_root():
    """
    Returns the directory where source is installed.  The directory is in the
    path so packages can be installed under it.
    """
    # We happen to know that the client pushed the temporary directory as the
    # first element of the path.
    assert isdir(sys.path[0])
    return sys.path[0]


def _handle_script(msg):
    # The client has already copied the script via SFTP and passes us the path to it.
    #
    # * modulename: The name of the module.
    # * filename: The path to it on this box.

    spec = importlib.util.spec_from_file_location(msg.modulename, msg.filename)
    module = importlib.util.module_from_spec(spec)

    sys.stdout = StringIO()
    sys.stderr = sys.stdout
    try:
        spec.loader.exec_module(module)
        sys.modules[msg.modulename] = module

        return dict(
            msgtype='script',
            modulename=msg.modulename,
            stdout=sys.stdout.getvalue()
        )
    except:
        return dict(msgtype='error', traceback=traceback.format_exc(),
                    stdout=sys.stdout.getvalue())
    finally:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__


def _handle_call(msg):
    module = sys.modules[msg.mname]
    try:
        func = getattr(module, msg.fname)
    except AttributeError as ex:
        return dict(msgtype='error', error='no attribute',
                    traceback=traceback.format_exc())

    sys.stdout = StringIO()
    sys.stderr = sys.stdout
    try:
        result = func(*msg.args, **msg.kwargs)
        return dict(msgtype='callret',
                    result=result,
                    stdout=sys.stdout.getvalue())
    except:
        return dict(msgtype='error', traceback=traceback.format_exc(),
                    stdout=sys.stdout.getvalue())
    finally:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__


def _handle_stat(msg):

    # 'exists isdir isfile size hash'

    results = {}

    if isdir(msg.filename):
        results['exists'] = True
        results['isdir']  = True
        results['isfile'] = False
    elif exists(msg.filename):
        results['exists'] = True
        results['isdir']  = False
        results['isfile'] = True
        results['size'] = os.path.getsize(msg.filename)
        results['hash'] = hash_file(msg.filename)

    results['msgtype'] = 'stat'
    results['filename'] = msg.filename

    return results
