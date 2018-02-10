'''
# Installation

Run

    pip install depflow

# Defining a process

Instantiate the flow with `flow = depflow.Depflow()`.  Define steps in the
process as nullary functions decorated with `@flow.depends(dep1, dep2, ...)`.
Dependencies can either be other steps or checks such as `depflow.file(path)`
and `depflow.file_hash(path)`.  Steps are run as they are defined.

# Creating new checks

Depflow accounts for two different types of dependency checks.

### Cached checks

Use `@depflow.check` to decorate a function that returns a value representing
the state of some resource, where a dependent step only needs to be updated if
the state of the resource changes.

Example:

    @depflow.check
    def kernel_version():
        return 'kernel-version', subprocess.check_output('uname -r')

or to account for command line arguments:

    flow = depflow.Depflow()
    parser = argparse.ArgumentParser()
    ...
    args = parser.parse_args()

    @depflow.check
    def args_hash(*keys):
        cs = hashlib.md5()
        for k in keys:
            cs.update(str(getattr(args, k)))
        return keys, cs.hexdigest()

    @flow.depends(arg_hash('output_dir', 'author'))
    def step_a():
        build_file('a.dat', args.output_dir, author=args.author)

    @flow.depends(arg_hash('output_dir'))
    def step_b():
        build_file('b.dat', args.output_dir, author='system')

Cached state is stored and compared based on a unique id generated from the
first return value, the step name and the ids of its other dependencies.

### Uncached checks

Use `@depflow.raw_check` to decorate a function that returns a boolean
indicating that the dependent step needs to be updated.

Example:

    flow = depflow.Depflow()

    @flow.raw_check
    def server_down(uri):
        return uri, not is_server_up(uri)

    @flow.depends(server_down('http://server1/state')):
    def server1_up():
        start_server('server1')

'''
import logging
import os
import time
import random
from hashlib import md5
import json
import json.scanner
import json.decoder
import sqlite3
import re
import abc
from functools import wraps


_random = random.SystemRandom()


def _coerce_tuple(v):
    if isinstance(v, list):
        return tuple(v)
    if isinstance(v, tuple):
        return v
    return (v,)


def _parse_array(*pargs, **kwargs):
    values, end = json.decoder.JSONArray(*pargs, **kwargs)
    return tuple(values), end


class _TupleDecoder(json.JSONDecoder):
    def __init__(self, *pargs, **kwargs):
        super().__init__(*pargs, **kwargs)
        self.parse_array = _parse_array
        self.scan_once = json.scanner.py_make_scanner(self)


def _loads(string):
    return json.loads(string, cls=_TupleDecoder)


class Dependency(abc.ABC):
    @abc.abstractmethod
    def unique(self, depflow):
        '''A unique identifier for this dependency.'''
        pass

    @abc.abstractmethod
    def dirty(self, step):
        '''
        Return true if the current state of this dependency does not
        match the previous state of the dependency relative to the step.
        '''
        pass

    @abc.abstractmethod
    def commit(self, step):
        '''
        Persist the new state of this dependency relative to the step.
        '''
        pass


class Step(Dependency):
    def __init__(self, depflow, function, nodes, qualification):
        self.depflow = depflow
        self._unique = (
            qualification,
            function.__name__,
            tuple(node.unique(depflow) for node in nodes)
        )
        self._changed = any(node.dirty(self) for node in nodes)
        if self._changed:
            depflow._logger.info('Running {}'.format(function.__name__))
            function()
            self._invocation = (int(time.time() * 1000), _random.random())
            depflow._db_set(self._unique, self._invocation)
            for node in nodes:
                node.commit(self)
        else:
            self._invocation = depflow._db_get(self._unique)

    def unique(self, depflow):
        return self._unique

    def dirty(self, step):
        changed = (
            self.depflow._db_get((self._unique, step.unique(self.depflow))) !=
            self._invocation
        )
        step.depflow._logger.info('Step dep: {}{}'.format(
            step.unique(step.depflow), ' (DIRTY)' if changed else ''))
        return changed

    def commit(self, step):
        self.depflow._db_set(
            (self._unique, step.unique(self.depflow)),
            self._invocation
        )


class Scope(object):
    def __init__(self, parent, qualification):
        self.parent = parent
        self.qualification = qualification

    def depends(self, *nodes, qualification=None):
        return self.parent.depends(
            *nodes,
            qualification=self.qualification + (qualification or ()))

    def scope(self, *qualification):
        return Scope(self, qualification)


class Depflow(object):
    def __init__(self, name='depflow'):
        '''
        (opt) `name` is the name of the flow.  This is used in logging
        and persisting the state of various checks are stored between runs in
        a database at `.{name}.sqlite3`.  The database filename can also be
        overridden with the environment variable `DEPFLOW_CACHE`.
        '''
        self._logger = logging.getLogger(name)
        _db_name = os.environ.get('DEPFLOW_CACHE', '.{}.sqlite3'.format(name))
        self._db = sqlite3.connect(_db_name)
        self._logger.debug(
            'Using cache at {}'.format(os.path.abspath(_db_name)))
        self._db.execute('create table if not exists keyvalue (key text primary key, value text not null)')  # noqa
        self._db.commit()

    def _db_get(self, key):
        key = json.dumps(key)
        out = self._db.execute(
            'select value from keyvalue where key = ?', (key,)).fetchone()
        if out is None:
            return None
        return _loads(out[0])

    def _db_set(self, key, value):
        key = json.dumps(key)
        value = json.dumps(value)
        self._db.execute(
            'insert or replace into keyvalue (key, value) values (?, ?)',
            (key, value))
        self._db.commit()

    def depends(self, *nodes, qualification=None):
        '''
        Runs the wrapped function if any dependency node has changed.

        Dependency `nodes` can be either other functions wrapped with depends
        or checks.

        When the step is used as a dependency for another step the function
        name is used to identify the state of this step.  If you have multiple
        steps with the same function name, you need to either specify
        the optional parameter `qualification` (as tuples and primitives)
        or use a `scope`.
        '''
        def wrap_function(function):
            return Step(self, function, nodes, qualification)
        return wrap_function

    def scope(self, *qualification):
        '''
        Returns a new scope with the specified `qualification`.  Scopes
        support all the same methods as `Depflow` but decorated steps
        will automatically receive these qualifications.

        Calling `scope` on a scope results in a new scope with the combined
        qualifications.
        '''
        return Scope(self, qualification)


def check(function):
    '''
    Converts a function that yields a `key` then `value` into a Dependency.

    The key is a unique id for the object being checked.  It is composed
    from tuples and primitives.

    The value represents the state of the object.  It is composed from tuples
    and primitives.  If the value changes compared to a previous invocation,
    the dependant method will run.

    ### Arguments

    `function` is the function to decorate.
    '''
    @wraps(function)
    def inner(*pargs, **kwargs):
        g = function(*pargs, **kwargs)

        class _Check(Dependency):
            def __init__(self):
                self.k = (function.__name__,) + _coerce_tuple(next(g))
                self.v = None

            def evaluate(self, depflow):
                try:
                    self.v = next(g)
                except StopIteration:
                    pass

            def unique(self, depflow):
                return self.k

            def dirty(self, step):
                self.evaluate(step.depflow)
                k = (self.k, step.unique(step.depflow))
                v_old = step.depflow._db_get(k)
                same = self.v == v_old
                step.depflow._logger.debug('Cached check: {}, {}{}'.format(
                    self.k, self.v, ' (DIRTY)' if same else ''))
                if same:
                    return False
                return True

            def commit(self, step):
                self.evaluate(step.depflow)
                k = (self.k, step.unique(step.depflow))
                step.depflow._db_set(k, self.v)

        return _Check()
    return inner


@check
def file(path):
    '''
    Check for changes in a single file by timestamp.

    ### Arguments

    `path` The path of the file.
    '''
    yield path
    yield int(os.path.getmtime(path) * 1000)


def _update_hash(path, cs):
    with open(path, 'rb') as source:
        while True:
            data = source.read(4096)
            if not data:
                break
            cs.update(data)


@check
def file_hash(path):
    '''
    Check for changes in a single file by hash.

    ### Arguments

    `path` The path of the file.
    '''
    yield path
    cs = md5()
    _update_hash(path, cs)
    yield cs.hexdigest()


def _tree(path, depth, ignore, start, update, finish):
    yield (path, depth)
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    ignore = [
        re.compile(pattern) if isinstance(pattern, str) else pattern
        for pattern in ignore or []
    ]
    if not path.endswith('/'):
        path = path + '/'
    state = start()
    for depth_, (root, dirs, files) in enumerate(os.walk(path)):
        if depth > 0 and depth_ > depth:
            break
        for file in files:
            full_file = os.path.join(root, file)
            if any(pattern.search(full_file) for pattern in ignore):
                continue
            state = update(state, full_file)
    yield finish(state)


@check
def tree(path, depth=0, ignore=None):
    '''
    Check for changes in a file tree by timestamp.

    ### Arguments

    `path` is the path of the root of the tree.

    (opt) `depth` indicates how many levels to descend into the path. 0 is
    unlimited, 1 is only the specified directory itself, 2 would include the
    first children, etc.

    (opt) `ignore` is a list of file and directory patterns to ignore.  Each
    pattern is a compiled regex applied against the file path from the tree
    root.
    '''
    return _tree(
        path,
        depth,
        ignore,
        lambda: 0,
        lambda state, path: state + os.path.getmtime(path),
        lambda state: state,
    )


@check
def tree_hash(path, depth=0, ignore=None):
    '''
    Check for changes in a file tree by hash.

    ### Arguments

    `path` is the path of the root of the tree.

    (opt) `depth` indicates how many levels to descend into the path. 0 is
    unlimited, 1 is only the specified directory itself, 2 would include the
    first children, etc.

    (opt) `ignore` is a list of file and directory patterns to ignore.  Each
    pattern is a compiled regex applied against the file path from the tree
    root.
    '''
    return _tree(
        path,
        depth,
        ignore,
        lambda: md5(),
        lambda state, path: _update_hash(path, state),
        lambda state: state.hexdigest(),
    )


def raw_check(function):
    '''
    Decorator that converts a function that yields a `key` then a `value` into
    a dependency.

    The `key` is a unique id for the object being checked.  It is composed
    from tuples and primitives.

    The `value` is True if the dependent should be updated, False otherwise.

    ### Arguments

    `function` is the function to decorate.
    '''
    @wraps(function)
    def inner(*pargs, **kwargs):
        g = function(*pargs, **kwargs)

        class _Check(Dependency):
            def __init__(self):
                self.k = (function.__name__,) + _coerce_tuple(next(g))
                self.v = None

            def evaluate(self, depflow):
                try:
                    self.v = next(g)
                except StopIteration:
                    pass

            def unique(self, depflow):
                return self.k

            def dirty(self, step):
                self.evaluate(step.depflow)
                step.depflow._logger.debug('Raw check: {}, {}{}'.format(
                    self.k, self.v, ' (DIRTY)' if self.v else ''))
                return self.v

            def commit(self, step):
                self.evaluate(step.depflow)

        return _Check()
    return inner


@raw_check
def no_file(path):
    '''
    Run the step if the specified file doesn't exist.

    ### Arguments

    `path` is the path of the file.
    '''
    yield path
    yield not os.path.exists(path)


__all__ = (
    'Depflow',
    'check',
    'raw_check',
    'file', 'file_hash',
    'tree', 'tree_hash',
    'no_file',
)
