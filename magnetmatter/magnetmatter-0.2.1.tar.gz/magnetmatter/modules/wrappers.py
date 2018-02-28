# wrappers.py

import sys
from datetime import datetime
from functools import wraps

def time_response(func, depth = ""):
    """
    use as a decoration to measure the execution time of the function call.
    """
    def function_wrapper(*args, **kwargs):
        t1 = datetime.now()
        print(depth + "#### " + func.__name__ + " ####")
        depth2 = depth + "    "
        res = func(*args, **kwargs)
        # print(res)
        t2 = datetime.now()
        print(depth + func.__name__ + " took " + str(t2-t1), " (hh:mm:ss.decimals)")
        return res
    return function_wrapper

class TraceCalls(object):
    """
    Use as a decorator on functions that should be traced. Several
    functions can be decorated - they will all be indented according
    to their call depth.
    """
    def __init__(self, stream=sys.stdout, indent_step=4, show_ret=False):
        self.stream = stream
        self.indent_step = indent_step
        self.show_ret = show_ret

        # This is a class attribute since we want to share the indentation
        # level between different traced functions, in case they call
        # each other.
        TraceCalls.cur_indent = 0

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            indent = '-' * TraceCalls.cur_indent
            argstr = ', '.join(
                #[repr(a) for a in args]) #+
                ["%s" % a for a, b in kwargs.items()])
            self.stream.write('%s> %s(%s)\n' % (indent, fn.__name__, argstr))

            TraceCalls.cur_indent += self.indent_step
            ret = fn(*args, **kwargs)
            TraceCalls.cur_indent -= self.indent_step

            if self.show_ret:
                self.stream.write('%s--> %s\n' % (indent, ret))
            return ret
        return wrapper
