from collections import Callable

import cffi
import logging
import six

from . import cstruct # import CStruct, CUnion, CStructType, CUnionType
from .functions import CFunction
from .typedef import CType
from .enums import wrapenum
from .ffi import FFI

if six.PY3:
    long = int


class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    def __getattr__(self, attr):
        return self.get(attr)
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def wrap(ffi, cobj):
    """
    Convenience function to wrap CFFI functions structs and unions.
    """
    if (isinstance(cobj, Callable)
        and ffi.typeof(cobj).kind == 'function'):
        cobj = CFunction(ffi, cobj)

    elif isinstance(cobj, ffi.CData):
        kind = ffi.typeof(cobj).kind
        if kind == 'pointer':
            kind = ffi.typeof(cobj).item.kind

        elif kind == 'array':
            cobj = [wrap(ffi, co) for co in cobj]

        if kind == 'struct':
            cobj = cstruct.CStruct(ffi, cobj)
        elif kind == 'union':
            cobj = cstruct.CUnion(ffi, cobj)

    elif isinstance(cobj, (int, long)):
        pass
    else:
        print("Unknown: %s" % cobj)
    return cobj


def wrapall(ffi=None, lib=None):
    """
    Convenience function to wrap CFFI functions structs and unions.

    Reads functions, structs and unions from an API/Verifier object and wrap
    them with the respective wrapper functions.

    :param ffi: The FFI object (needed for it's ``typeof()`` method)
    :param lib: As returned by ``ffi.dlopen()`` or attribute of built library

    Returns a dict mapping object names to wrapper instances. Hint: in
    a python module that only does CFFI boilerplate and verification, etc, try
    something like this to make the C values available directly from the module
    itself::

        globals().update(wrapall(myffi, mylib))

    """

    # TODO: Support passing in a checkerr function to be called on the
    # return value for all wrapped functions.

    ffi = ffi if ffi is not None else \
        lib.ffi if hasattr(lib, 'ffi') else FFI()

    libname = lib.__name__.rstrip('.lib')
    cobjs = type(libname, (dotdict,), {})()
    cobjs.__name__ = libname
    cobjs.ffi = FFI(ffi)
    for attr in dir(lib):
        if not attr.startswith('_'):
            cobj = getattr(lib, attr)
            cobj = wrap(ffi, cobj)
            cobjs[attr] = cobj

        # The things I go through for a little bit of introspection.
        # Just hope this doesn't change too much in CFFI's internals...

    try:
        typedef_names, names_of_structs, names_of_unions = ffi.list_types()
        for ctypename in names_of_structs:
            try:
                cobjs[ctypename] = cstruct.CStructType(ffi, ctypename)
            except ffi.error as ex:
                pass
        for ctypename in names_of_unions:
            try:
                cobjs[ctypename] = cstruct.CUnionType(ffi, ctypename)
            except ffi.error as ex:
                pass
        for ctypename in typedef_names:
            try:
                cobjs[ctypename] = CType(ffi, ctypename)
                try:
                    typeof = ffi.typeof(ctypename)
                    if typeof.kind == 'enum':
                        for val, name in six.iteritems(typeof.elements):
                            cobjs[name] = wrapenum(val, typeof)

                    elif typeof.kind == 'struct':
                        cobjs[ctypename] = cstruct.CStructType(ffi, ctypename)

                    elif typeof.kind == 'union':
                        cobjs[ctypename] = cstruct.CUnionType(ffi, ctypename)

                except AttributeError:
                    pass
            except ffi.error:
                logging.debug('Could not parse typedef "%s"', ctypename)

    except AttributeError:
        try:
            decls = ffi._parser._declarations
        except AttributeError:
            decls = {}
        for _, ctype in decls.items():
            if isinstance(ctype, cffi.model.StructType):
                cobjs[ctype.get_c_name()] = cstruct.CStructType(ffi, ctype)
            elif isinstance(ctype, cffi.model.UnionType):
                cobjs[ctype.get_c_name()] = cstruct.CUnionType(ffi, ctype)

    return cobjs