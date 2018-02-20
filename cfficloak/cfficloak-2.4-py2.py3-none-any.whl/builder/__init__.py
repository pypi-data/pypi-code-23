import io
import re
import sys
import types
import wrapt
from collections import namedtuple
from cfficloak.functions import CFunction
try:
    from pathlib2 import Path
except ImportError:
    from pathlib import Path

third_party = str((Path(__file__).parent / 'third-party').resolve())
if third_party not in sys.path:
    sys.path.append(third_party)

import pcpp

# Trap definitions as ffibuilder.cdef is run for use in generating definitions file
functions = []
defines = {}


fndef = namedtuple('c_function', ['decl', 'args', 'rettype'])


@wrapt.patch_function_wrapper('cffi.cparser', 'Parser._add_constants')
def wrap_Parser__add_constants(wrapped, instance, args, kwargs):
    global defines
    if args:
        defines[args[0]] = args[1]
    else:
        defines[kwargs['key']] = kwargs['val']
    return wrapped(*args, **kwargs)


@wrapt.patch_function_wrapper('cffi.cparser', 'Parser._declare_function')
def wrap_Parser__declare_function(wrapped, instance, args, kwargs):
    global functions
    if args:
        tp, quals, decl = args
    else:
        tp, quals, decl = kwargs['tp'], kwargs['quals'], kwargs['decl']
    functions.append(fndef(decl, tp.args, tp.result))
    return wrapped(*args, **kwargs)


# Details used for generating definitions file
template_header = '''\
# Auto-generated file.

import cfficloak
import {libname}

from {libname} import ffi, lib as _lib
lib = cfficloak.wrapall(ffi, _lib)
'''


template_fn = '''\
@cfficloak.function_skeleton(cmodule=lib, noret=False, outargs=[])
def {name}({args}):
    """
    {desc}
{params}
    :returns: {rettype}
    """


'''
template_param = '''\
    :param {argtype} {argname}: {argdesc}'''


Comment = namedtuple('comment', ['prev', 'current', 'next'])


def generate_definitions_file(definitions_file, libname, comments_callback=None):
    comments_callback = comments_callback or (lambda x: '')
    _skelfile = Path(definitions_file)

    _skelfile.open('a').close()  # Ensure file exists
    existing = _skelfile.read_text().split("# Functions")[-1].strip()

    with _skelfile.open('w') as skelfile:
        skelfile.write(template_header.format(libname=libname))

        skelfile.write("\n# Defines")
        for d, t in defines.items():
            definition = "{d} = lib.{d}  # type: {t}".format(d=d, t=type(t).__name__)
            c = comments_callback(d)

            if c and isinstance(c, str):
                c = Comment(None, c, None)

            if c and isinstance(c, Comment):
                if c.prev:
                    skelfile.write('\n\n# %s' % c.prev)
                skelfile.write('\n%s' % definition)
                if c.current:
                    skelfile.write(' # ' + c.current)
                if c.next:
                    skelfile.write('\n# %s' % c.next)
            else:
                skelfile.write('\n%s' % definition)

        skelfile.write("\n\n\n# Functions\n\n")
        if existing:
            skelfile.write(existing)
            skelfile.write('\n\n\n')

        for func in functions:  # type: fndef

            if "def %s" % func.decl.name in existing:
                continue

            args = []
            params = []
            for idx, arg in enumerate(func.args):
                argname = func.decl.type.args.params[idx].name
                argdesc = str(arg)
                while hasattr(arg, 'totype'):
                    arg = arg.totype
                argtype = arg.name
                params.append(template_param.format(argtype=argtype,
                                                    argname=argname,
                                                    argdesc=argdesc))
                args.append(argname)

            rettype = 'None' if func.rettype == 'void' else func.rettype.name

            c = comments_callback(func.decl.name)
            if c and isinstance(c, str):
                c = Comment(None, c, None)
            if not c:
                c = Comment(None, None, None)

            fn_skel = template_fn.format(name=func.decl.name,
                                         args=', '.join(args),
                                         desc=c.current if c.current else func.decl.name,
                                         params='\n'.join(params),
                                         rettype=rettype)
            if c.prev:
                skelfile.write('# %s\n\n' % c.prev)
            skelfile.write(fn_skel)


def import_file(filename):
    """
    Import a module directly from a filename, without touching sys.path
    :param str, Path filename: path to module to import
    :return: module
    """

    PY2 = sys.version_info.major == 2
    if PY2:
        import imp
        mod = imp.load_source('clib', str(filename))
    else:
        import importlib.machinery
        loader = importlib.machinery.SourceFileLoader('clib', str(filename))
        mod = types.ModuleType(loader.name)
        loader.exec_module(mod)
    return mod


# The original _parse_error raises an exception during cdef parsing and
# stops the cdef operation. This will capture the error and let it continue
# trying to parse the rest of the file

# TODO this is completely not thread-safe!
errors = []
# import pycparser.plyparser
# class PLYParser(pycparser.plyparser.PLYParser):
#
#     def _parse_error(self, msg, coord):
#         global errors
#         errors.append((coord, msg))
#
# pycparser.plyparser.PLYParser._parse_error = PLYParser._parse_error
#
# import pycparser.c_parser
# pycparser.c_parser.CParser.p_error = lambda self, x: x

# import pycparser.ply.yacc
# # Utility function to call the p_error() function with some deprecation hacks
# _orig_call_errorfunc = pycparser.ply.yacc.call_errorfunc
# def call_errorfunc(errorfunc, token, parser):
#     try:
#         parser.errorok = True
#         _orig_call_errorfunc(errorfunc, token, parser)
#     except Exception as ex:
#         global errors
#         errors.append(ex)
#     return token
#
# pycparser.ply.yacc.call_errorfunc = call_errorfunc


class Preprocessor(pcpp.Preprocessor):
    def on_directive_handle(self, directive, toks, ifpassthru):
        super(Preprocessor, self).on_directive_handle(directive, toks, ifpassthru)
        return None  # Pass through macros

    def on_comment(self, tok):
        return  # Pass through comments


def parse_header(content=None, filename=None, includes=None):
    """
    Runs the content (if provided) then the read file (if provided)
     through the c preprocessor.
    :param str, bytes content: header content to process
    :param filename: header file to read
    :param list,tuple,set includes: list of include dirs to add to search path
    :return: bytes
    """
    if not any((filename, content)):
        raise ValueError("Must provide filename or content")
    filename = Path(filename)
    content = '\n'.join(((content or ""), filename.read_text()))
    pp = Preprocessor()
    pp.add_path(str(Path(__file__).parent / 'include'))
    if includes:
        for include in includes:
            pp.add_path(str(include))
    pp.parse(content)
    out = io.StringIO()
    pp.write(out)
    parsed = out.getvalue()
    parsed = re.sub(r'^\s*#\s*(line|include).*\n', '', parsed, flags=re.MULTILINE)
    return parsed



