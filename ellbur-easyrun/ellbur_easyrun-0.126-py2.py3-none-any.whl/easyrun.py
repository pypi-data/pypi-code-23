
from __future__ import print_function
from quickfiles import *
from quickstructures import *
from subprocess import *
from collections import namedtuple as nt

def easyrun(*cmd, **kwargs):
    echo = kwargs.get('echo', True)
    echo_output = kwargs.get('echo_output', True)
    @easyrunto(cmd, **kwargs)
    def result(proc):
        output = ''
        for line in proc.stdout:
            if echo and echo_output:
                print(line, end='')
                sys.stdout.flush()
            output += line
        return output
    return result

def easyrun_as_proc(*cmd, **kwargs):
    echo = kwargs.get('echo', True)
    echo_output = kwargs.get('echo_output', True)
    wd = kwargs.get('wd', None)
    return run_as_proc(clean(cmd, wd), **kwargs)

def easyrunto(*cmd, **kwargs):
    wd = kwargs.get('wd', None)
    return runto(clean(cmd, wd), **kwargs)

def easyruntty(*cmd, **kwargs):
    wd = kwargs.get('wd', None)
    return runtty(clean(cmd, wd), **kwargs)

class SINK(nt('SINK', ['extension'])):
    pass

def clean(cmd, wd=None, first=True):
    cleaned = []
    for c in cmd:
        if isinstance(c, Path):
            c.make_parents()
        
        if isinstance(c, SINK):
            cleaned.append(c)
        elif isinstance(c, Path):
            if wd != None:
                cleaned.append(c.against(wd))
            else:
                try:
                    cleaned.append(str(c))
                except UnicodeEncodeError:
                    cleaned.append(unicode(c))
        elif isinstance(c, list) or isinstance(c, tuple):
            cleaned.extend(clean(c, wd=wd, first=first))
        else:
            try:
                cleaned.append(str(c))
            except UnicodeEncodeError:
                cleaned.append(unicode(c))
        
        first = False
        
    return t(cleaned)

def runto(cmd, wd=None, stderr=None, verbose=False, echo=True, known_as=None, echo_output=None):
    if echo and not verbose:
        if known_as:
            print('\033[34m' + known_as + '\033[0m', file=sys.stderr) # ]]
        else:
            print('\033[34m' + abbrev(cmd) + '\033[0m', file=sys.stderr) # ]]
    elif echo:
        print('\033[34m' + str(cmd) + ' (in ' + str(wd) + ')' + '\033[0m', file=sys.stderr) # ]]
    stdout_arg = None if echo_output else PIPE
    proc = Popen(cmd, stdin=PIPE, stdout=stdout_arg, stderr=stderr, cwd=(str(wd) if wd!=None else None))
    def next(f):
        result = f(proc)
        status = proc.wait()
        if status != 0:
            raise RunFailed(' '.join(cmd) + ' returned ' + str(status) + ' exit status.')
        return result
    return next

def run_as_proc(cmd, wd=None, stderr=None, verbose=False, echo=True, known_as=None, echo_output=None):
    if echo and not verbose:
        if known_as:
            print('\033[34m' + known_as + '\033[0m', file=sys.stderr) # ]]
        else:
            print('\033[34m' + abbrev(cmd) + '\033[0m', file=sys.stderr) # ]]
    elif echo:
        print('\033[34m' + str(cmd) + ' (in ' + str(wd) + ')' + '\033[0m', file=sys.stderr) # ]]
    stdout_arg = None if echo_output else PIPE
    return Popen(cmd, stdin=PIPE, stdout=stdout_arg, stderr=stderr, cwd=(str(wd) if wd!=None else None))

def runtty(cmd, wd=None, verbose=False, echo=True):
    if echo and not verbose:
        print('\033[34m' + abbrev(cmd) + '\033[0m', file=sys.stderr) # ]]
    elif echo:
        print('\033[34m' + str(cmd) + ' (in ' + str(wd) + ')' + '\033[0m', file=sys.stderr) # ]]
    try:
        proc = Popen(cmd, cwd=(str(wd) if wd!=None else None))
    except OSError as e:
        if e.errno == 2:
            if len(cmd) > 0:
                raise RunFailed('Could not find %s' % (cmd[0],))
            else:
                raise RunFailed('Empty command failed to run')
        else:
            raise e
    status = proc.wait()
    if status != 0:
        raise RunFailed(' '.join(cmd) + ' returned ' + str(status) + ' exit status.')

def abbrev(cmd):
    return p(cmd[0]).name + ' ... ' + ' '.join(p(_).name
        for _ in cmd[1:] if not startswithunicode(_, '-'))

def startswithunicode(string, prefix):
    try:
        return string.startswith(prefix)
    except UnicodeEncodeError:
        try:
            return unicode(string, 'utf-8').startswith(prefix)
        except UnicodeDecodeError:
            return False

class RunFailed(Exception):
    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg
    def __repr__(self): return self.msg
    def __str__(self): return self.msg
    
def spy(hl, into=sys.stdout):
    from fcntl import fcntl, F_GETFL, F_SETFL
    from select import select
    import os, sys

    flags = fcntl(hl, F_GETFL)
    fcntl(hl, F_SETFL, flags | os.O_NONBLOCK)

    all = ''

    while True:
        select([hl], [], [])
        data = hl.read()
        if len(data) == 0: break
        into.write(data)
        into.flush()
        all = all + data
    
    return all

