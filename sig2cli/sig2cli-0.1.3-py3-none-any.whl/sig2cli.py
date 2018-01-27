from __future__ import print_function
import inspect
import argparse
from funcsigs import Parameter, signature
import re
from functools import wraps
import sys

def sig2cli(fn):
    """Decorator that transforms the signature of a function to the input of an argument parser.
    It lets you define a function signature instead of writing a lot of verbose argparse code.
    Keyword arguments are the default.
    The command line description is taken from the docstring of the method, with the following conventions:
        - the description is everything that precedes the string "Arg" (so Arguments, Args) that starts the argument list.
        - each argument should be in the format <argname> : [argtype] <argumentdescription>
    The type is inferred from default arguments, or taken from the docstring if specified. Allowed types are "str", "int", "float", "bool".
    It supports short args (the first letter of each argument) only if they are all different and no argument starts with "h" (reserved for help)
    Default bool arguments are registered as flags.

    The decorated function should then be called with sys.argv[1:] as the argument.

    Example
        @sig2cli
        def a(first,second=0,third=0):
            '''Just a simple example

            Args:
                first : int. An int 
                second : int. Another int
                third : int. Yet another int
            '''
            return first + second + third
        
        assert a(['--first', '5']) == 5
        assert a(['--first', '5', '--second', '3']) == 8

    Arguments
        fn : function, The function to be changed

    Returns
        The function with the updated signature.
    """
    _types_dict = {
        'str':str,
        'int':int,
        'float':float,
        'bool':bool
    }
    sig = signature(fn)
    non_defaults = [x for x,v in sig.parameters.items() if v.default == Parameter.empty]
    defaults = {k:v.default for k,v in sig.parameters.items() if v.default != Parameter.empty}
    doc = fn.__doc__
    descr = re.findall(r'^([\s\S]*)\s+Arg', doc.strip()) if doc else ''
    parser = argparse.ArgumentParser(description=descr[0] if len(descr)>0 else '')
    par_type = {}
    par_help = {}
    if doc:
        par_typename = dict(re.findall(r'(\w+)\s*:(?!\n)\s*(\w+)', doc))
        par_type = {k:_types_dict[v] for k,v in par_typename.items() if v in _types_dict and k in non_defaults}
        par_help = dict(re.findall(r'(\w+)\s*\:(?!\n)\s*(.*)', doc))
    # check that all the starting letters are different
    initials = set(x[0] for x in sig.parameters.keys())
    easy_short_args = len(initials) == len(sig.parameters.keys())
    # "h" is reserved for help
    easy_short_args = easy_short_args and 'h' not in initials
    for nd in non_defaults:
        names = ('-'+nd[0], '--'+nd) if easy_short_args else ('--'+nd,) 
        parser.add_argument(*names, required=True, type=par_type.get(nd, str), help=par_help.get(nd, ''))
    for d,v in defaults.items():
        names = ('-'+d[0], '--'+d) if easy_short_args else ('--'+d,) 
        default_str = ' (default: {})'.format(v)
        if type(v) == bool:
            action = 'store_false' if v else 'store_true'
            parser.add_argument(*names, action=action, help=par_help.get(d, '')+default_str)
        else:
            parser.add_argument(*names, default=v, type=type(v), help=par_help.get(d, '')+default_str)
    @wraps(fn)
    def wrapped(argv):
        opt, _ = parser.parse_known_args(argv)
        mem = inspect.getmembers(opt)
        kwargs = {x[0]:x[1] for x in mem if not x[0].startswith('_')}
        return fn(**kwargs)
    return wrapped

def run(fn):
    """run a function taking the arguments from the command line.
    """
    a_fn = sig2cli(fn)
    a_fn(sys.argv[1:])

if __name__ == '__main__':
    #'''
    @sig2cli
    def a(first,second=0,third=0):
        """Just a simple example

        Args:
            first : int. An int 
            second : int. Another int
            third : int. Yet another int
        """
        return first + second + third

    assert a(['--first', '5']) == 5
    assert a(['--first', '5', '--second', '3']) == 8
    assert a(['--first', '5', '--second', '3', '--third', '-4']) == 4
    help_str = """usage: sig2cli.py [-h] --first FIRST [--second SECOND] [--third THIRD]

Just a simple example

optional arguments:
  -h, --help       show this help message and exit
  --first FIRST    int. An int
  --second SECOND  int. Another int
  --third THIRD    int. Yet another int
"""
    #assert help_str == a(['-h'])
    #'''

    #'''
    def hi(name, times=1, enthusiast=False):
        """Say hi!
        Arguments
            name:       person to greet
            times:      how many times to greet
            enthusiast: add an exclamation mark at the end
        """
        for _ in range(times):
            print('Hi {}{}'.format(name, '!' if enthusiast else ''))

    run(hi)
    #'''
