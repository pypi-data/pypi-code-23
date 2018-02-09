# -*- coding: utf-8 -*-
# @Author: Cody Kochmann
# @Date:   2018-02-09 11:56:09
# @Last Modified 2018-02-09
# @Last Modified time: 2018-02-09 15:16:34

from functools import wraps
import os
import logging

def valid_context_manager(potential_ctx):
    ''' returns true if the input is a valid context manager '''
    return hasattr(
        potential_ctx, '__enter__'
    ) and callable(
        potential_ctx.__enter__
    ) and hasattr(
        potential_ctx, '__enter__'
    ) and callable(
        potential_ctx.__enter__
    )

def also_a_decorator(context_class):
    if not valid_context_manager(context_class): raise TypeError('also_a_decorator needs a valid context manager')

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            with self:
                return fn(*args, **kwargs)
        return wrapper

    context_class.__call__ = __call__

    return context_class

@also_a_decorator
class pushd(object):
    ''' This is a replica of bash's pushd command. In the context manager, the
        console moves over to the target directory. When the context exits, you
        return to the previous directory.
    '''
    def __init__(self, target):
        self.target = target
        self.saved = ''

    def __enter__(self):
        self.saved = os.getcwd()
        os.chdir(self.target)
        return self.target

    def __exit__(self, exctype, excinst, exctb):
        os.chdir(self.saved)
        if excinst is None:
            return True
        else:
            raise excinst

@also_a_decorator
class logged_exceptions(object):
    ''' running your code in this context manager is the equivalent of:

            try:
                {your_code}
            except Exception as ex:
                logging.exception(ex)

        which allows you to write functions in a server that wont actually
        kill the server if something goes wrong, but at the same time will
        log if there was an error

        This is an important piece to use in the threaded portions because
        it brings locality to the tracebacks. This prevents the threading
        library from hiding where the blowup was by logging inside the crashing
        thread instead of raising the traceback to the main thread.

        Without this you will wind up with tracebacks that make things look like
        stuff blew up in thread mystery land.
    '''
    def __init__(self, logger_function=logging.exception):
        ''' this allows logged_exceptions to work as a decorator '''
        if not callable(logger_function): raise TypeError('logger_function needs to be a callable function')
        self.logger_function = logger_function

    def __enter__(self):
        pass

    def __exit__(self, exctype, excinst, exctb):
        if excinst is not None: # if things ran cleanly, excinst is None
            self.logger_function(excinst)  # log if there was an error
        return True             # allow the program to continue on

if __name__ == '__main__':
    print('testing context manager usage')
    with pushd('/tmp') as d:
        print(d)
        with logged_exceptions():
            print(d*3.0)

    print('testing decorator usage')

    @logged_exceptions()
    @pushd('/tmp')
    def my_adder(a,b):
        print(os.getcwd())
        print(a+b)

    my_adder(1,2)
    my_adder(5.0,None)

    print('test complete')
