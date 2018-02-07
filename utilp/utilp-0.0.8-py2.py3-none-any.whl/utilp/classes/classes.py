"""Common usefull Python3 classes."""

import os
import time
import random
import logging
import threading
from functools import partial
import traceback
import sys
import collections.abc

from tqdm import tqdm


class Bunch(dict):
    """A dict usable with dot notation.

    Example
    -------
    >>> bunch = Bunch()
    >>> bunch.a = 5
    >>> print(bunch.a)
    5
    """
    def __init__(self, **kw):
        dict.__init__(self, kw)
        self.__dict__ = self\


class StringEnum(collections.abc.Sequence):
    """Easy, ordered enum-like objects from String lists.

    Arguments
    ---------
    members : list
        A list of strings,

    Example
    -------
    >>> colors = StringEnum(['Red', 'Blue', 'Green'])
    >>> colors.Red
    'Red'
    """
    def __init__(self, members):
        self.members = members
        for name in members:
            setattr(self, name, name)
    def __getitem__(self, index):
        return self.members[index]
    def __len__(self):
        return len(self.members)
    def __repr__(self):
        return str(self.members)


class Singleton(type):
    """A meta-class for singleton classes.

    Make your class a singleton using the following pattern:
    # In Python2:
    class MyClass(BaseClass):
        __metaclass__ = Singleton

    # In Python3
    class MyClass(BaseClass, metaclass=Singleton):
        pass
    """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


# ==== Start of InheritableDocstrings ==== #
# Code taken from thie recepie: http://code.activestate.com/
# recipes/578587-inherit-method-docstrings-without-breaking-decorat/

def mro(*bases):
    """Calculate the Method Resolution Order of bases using the C3 algorithm.

    Suppose you intended creating a class K with the given base classes. This
    function returns the MRO which K would have, *excluding* K itself (since
    it doesn't yet exist), as if you had actually created the class.

    Another way of looking at this, if you pass a single class K, this will
    return the linearization of K (the MRO of K, *including* itself).

    Found at:
    http://code.activestate.com/recipes/577748-calculate-the-mro-of-a-class/
    """
    seqs = [list(C.__mro__) for C in bases] + [list(bases)]
    res = []
    while True:
        non_empty = list(filter(None, seqs))
        if not non_empty:
            # Nothing left to process, we're done.
            return tuple(res)
        for seq in non_empty:  # Find merge candidates among seq heads.
            candidate = seq[0]
            not_head = [s for s in non_empty if candidate in s[1:]]
            if not_head:
                # Reject the candidate.
                candidate = None
            else:
                break
        if not candidate:
            raise TypeError("inconsistent hierarchy, no C3 MRO is possible")
        res.append(candidate)
        for seq in non_empty:
            # Remove candidate.
            if seq[0] == candidate:
                del seq[0]


# This definition is only used to assist static code analyzers
def copy_ancestor_docstring(func):  # pylint: disable=W0613
    """Copy docstring for method from superclass.
    For this decorator to work, the class has to use the
    `InheritableDocstrings` metaclass.
    """
    raise RuntimeError('Decorator can only be used in classes '
                       'using the `InheritableDocstrings` metaclass')


def _copy_ancestor_docstring(mro_list, func):  # pylint: disable=W0613
    """Decorator to set docstring for *func* from *mro*"""
    if func.__doc__ is not None:
        raise RuntimeError('Function already has docstring')
    # Search for docstring in superclass
    for cls in mro_list:
        super_fn = getattr(cls, func.__name__, None)
        if super_fn is None:
            continue
        func.__doc__ = super_fn.__doc__
        break
    else:
        raise RuntimeError("Can't inherit docstring for %s: method does not "
                           "exist in superclass" % func.__name__)
    return func


class InheritableDocstrings(type):
    """Allows inheritance of doc strings from ancestor methods.

    Make your class inherit docstrings using the following pattern:

    from utilp.class import (
        InheritableDocstrings,
        copy_ancestor_docstring
    )

    class MyClass(BaseClass, metaclass=InheritableDocstrings):

        @copy_ancestor_docstring
        def overriding_method(self):
            pass
    """

    @classmethod
    def __prepare__(cls, name, bases, **kwds):
        classdict = super().__prepare__(name, bases, *kwds)

        # Inject decorators into class namespace
        classdict['copy_ancestor_docstring'] = partial(
            _copy_ancestor_docstring, mro(*bases))

        return classdict

    def __new__(cls, name, bases, classdict):
        # Decorator may not exist in class dict if the class (metaclass
        # instance) was constructed with an explicit call to `type`.
        # (cf http://bugs.python.org/issue18334)
        if 'copy_ancestor_docstring' in classdict:
            # Make sure that class definition hasn't messed with decorators
            copy_impl = getattr(
                classdict['copy_ancestor_docstring'], 'func', None)
            if copy_impl is not _copy_ancestor_docstring:
                raise RuntimeError(
                    'No copy_ancestor_docstring attribute may be created '
                    'in classes using the InheritableDocstrings metaclass')
            # Delete decorators from class namespace
            del classdict['copy_ancestor_docstring']
        return super().__new__(cls, name, bases, classdict)

# ==== End of InheritableDocstrings ==== #


# ==== Start of PrintLogger ==== #

class PrintLogger():
    """A simple logger that can also print each message to screen.

    Logs are saved in the ~/neura_logs directory by default. A different
    directory can be set by setting the NEURA_LOGS_DIR environment variable.
    """

    NEURA_LOGS_DIR_ENV_VAR = 'NEURA_LOGS_DIR'
    LOGDIR_FROM_ENV = os.environ.get('NEURA_LOGS_DIR')
    DEFAULT_LOGDIR = '{}/neura_logs'.format(os.path.expanduser("~"))
    LOGDIR = LOGDIR_FROM_ENV or DEFAULT_LOGDIR
    TIMESTR = time.strftime("%Y%m%d-%H%M%S")

    def __init__(self, log_name, verbose=False, writelog=True, debug=False):
        self.log_name = log_name
        self.verbose = verbose
        self.writelog = writelog
        self.debugmode = debug
        if self.writelog:
            self.logger = logging.getLogger(log_name)
            os.makedirs(PrintLogger.LOGDIR, exist_ok=True)
            logging.basicConfig(
                filename='{}/neura_python_{}.log'.format(
                    PrintLogger.LOGDIR, PrintLogger.TIMESTR),
                filemode='a',
                level=logging.INFO
            )
        else:
            self.logger = None

    def set_verbosity(self, boolean):
        """If set to True, the printlog() method will print to screen."""
        self.verbose = boolean

    def is_verbose(self):
        """Returns the verbosity state of this PrintLogger."""
        return self.verbose

    def print(self, string, verbose=None):
        """Prints the given string to screen if verbosity is on."""
        if verbose or self.verbose:
            print(string)

    def set_logging(self, boolean):
        """If set to True, the printlog() method will log to screen."""
        self.writelog = boolean

    def is_logging(self):
        """Returns the logging state of this PrintLogger."""
        return self.writelog

    def log(self, string):
        """Prints the given string to a logfile."""
        if self.writelog:
            self.logger.info(string)

    def printlog(self, string, verbose=None, flush=False):
        """Prints the given string to a logfile if logging is on, and to
        screen if verbosity is on."""
        if self.writelog:
            self.logger.info(string)
        if verbose or (self.verbose and verbose is None):
            print(string, flush=flush)

    def exception(self, exception):
        """Prints the stacktrace of the given exception."""
        if self.writelog:
            self.logger.exception(exception)
        if self.verbose:
            for line in  traceback.format_exception(
                    None, exception, exception.__traceback__):
                print(line, end='', file=sys.stderr, flush=True)


    def debug(self, string):
        """Behaves like printlog if debug was set to True. Otherwise does
        nothing."""
        if self.debugmode:
            self.printlog(string)

    def tqdm(self, iterable, **kwargs):
        """Wraps the given iterable with a tqdm progress bar if this logger is
        set to verbose. Otherwise, returns the iterable unchanged."""
        if 'disable' in kwargs:
            kwargs.pop('disable')
        return tqdm(iterable, disable=not self.verbose, **kwargs)

# ==== End of PrintLogger ==== #


# ==== Threading ==== #

class ResultReducerThread(threading.Thread):
    """A thread reducing partial results from a queue."""

    def __init__(self, name, res_queue, reducer, verbose=False, interval=500):
        super(ResultReducerThread, self).__init__()
        self.name = name
        self.res_queue = res_queue
        self.reducer = reducer
        self.result = None
        self.verbose = verbose
        self.interval = interval
        self.count = 0

    def run(self):
        while True:
            if not self.res_queue.empty():
                partial_result = self.res_queue.get()
                if partial_result is None:  # this is a signal that we're done
                    self.res_queue.put(self.result)
                    return
                self.result = self.reducer(self.result, partial_result)
                if self.verbose:
                    self.count += 1
                    if self.count % self.interval == 0:
                        print('{} partial results reduced.'.format(self.count))
            time.sleep(random.random())
