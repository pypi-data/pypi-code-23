from __future__ import absolute_import
import re
from functools import wraps

import six

from .arrays import numpy
from .enums import wrapenum
from .arrays import nparrayptr
from array import array

class NullError(Exception):
    pass


class outarg(object):
    """
    When setting outargs=[0,1,2] on function_skeleton/cmethod, the integer
     for each outarg can be replaced with an instance of this class to provide
     extra automatic type handling
    """
    def __init__(self, argi, ffitype=None, converter=None):
        if isinstance(argi, outarg):
            self.argi = argi.argi
            self.ffitype = argi.ffitype
            self.converter = argi.converter
            self.inout = argi.inout
        else:
            self.argi = argi
            self.ffitype = ffitype
            self.converter = converter
            self.inout = None

    def outtype(self, inout):
        self.inout = inout
        return self

    def __lt__(self, other):
        if isinstance(other, outarg):
            return self.argi < other.argi
        else:
            return self.argi < other


def function_skeleton(cmodule=None, outargs=(), inoutargs=(), arrays=(), retargs=None,
           checkerr=None, noret=False, doc=None):
    """
    This can be used as a decorator on a function stub to declare a python skeleton for a c function
    eg:
        @function_skeleton(cmodule=_built_cmodule, checkerr=_checkerr, noret=True, outargs=[])
        def c_functtion_name(args1, arg2):
            \"""
             c function docstring/description.

             :param type_of_arg1 arg1: arg1 does this
             :param type_of_arg2 arg2: arg2 does this

             :return something useful
             \"""
            pass

        @function_skeleton(cmodule=_wrapped, noret=True, outargs=[outarg(0, "wchar_t[100]" , ffi.string)])
        def c_function_that_takes_buffer_defined_as_wchar*():
            \"""
            :return str: up to 100 characters long
            \"""

    :param cmodule: api/module to get c method from
    :param outargs: as per cmethod below
    :param inoutargs: as per cmethod below
    :param arrays: as per cmethod below
    :param retargs: as per cmethod below
    :param checkerr: as per cmethod below
    :param noret: as per cmethod below
    :param doc: as per cmethod below

    """
    @wraps(cmethod)
    def cmethod_wrap(func):
        cfunc = getattr(cmodule, func.__name__)
        defaults = func.__defaults__
        return cmethod(cfunc=cfunc, outargs=outargs, inoutargs=inoutargs, arrays=arrays,
                       retargs=retargs, checkerr=checkerr, noret=noret, doc=doc, defaults=defaults)
    return cmethod_wrap


def cmethod(cfunc, outargs=(), inoutargs=(), arrays=(), retargs=None,
           checkerr=None, noret=False, doc=None, defaults=None):
    """ Wrap cfunc to simplify handling outargs, etc.

    This feature helps to simplify dealing with pointer parameters which
    are meant to be "return" parameters. If any of these are specified, the
    return value from the wrapper function will be a tuple containing the
    actual return value from the C function followed by the values of the
    pointers which were passed in. Each list should be a list of parameter
    position numbers (0 for the first parameter, etc)..

    * ``outargs``: These will be omitted from the cmethod-wrapped function
      parameter list, and fresh pointers will be allocated (with types
      derived from the C function signature) and inserted in to the
      arguments list to be passed in to the C function. The pointers will
      then be dereferenced and the value included in the return tuple.

    * ``inoutargs``: Arguments passed to the wrapper function for these
      parameters will be cast to pointers before being passed in to the C
      function. False can be passed to the wrapper function to act like an
      outarg however at end use. Pointers will be unboxed in the return tuple.

    * ``arrays``: Arguments to these parameters can be python lists or
      tuples, numpy arrays or integers.

      * Python lists/tuples will be copied in to newly allocated CFFI
        arrays and the pointer passed in. The generated CFFI array will be
        in the return tuple.

      * Numpy arrays will have their data buffer pointer cast to a CFFI
        pointer and passed in directly (no copying is done). The CFFI
        pointer to the raw buffer will be returned, but any updates to the
        array data will also be reflected in the original numpy array, so
        it's recommended to just keep using that. (TODO: This behavior may
        change to remove these CFFI pointers from the return tuple or maybe
        replace the C array with the original numpy object.)

      * Integers will indicate that a fresh CFFI array should be allocated
        with a length equal to the int and initialized to zeros. The generated
        CFFI array will be included in the return tuple.

    * ``retargs``: (Not implemented yet.) A list of values to be returned from
      the cmethod-wrapped function. Normally the returned value will be a tuple
      containing the actual return value of the C function, followed by the
      final value of each of the ``outargs``, ``inoutargs``, and ``arrays`` in
      the order they appear in the C function's paramater list.

    * ``noret``: don't return cfunc's ret. Useful when checkerr is handling this instead

    * ``doc``: Optional string/object to attach to the returned function's docstring

    * ``defaults``: Optional iterable of default args in reverse order

    As an example of using ``outargs`` and ``inoutargs``, a C function with
    this signature::

        ``int cfunc(int inarg, int *outarg, float *inoutarg);``

    with an ``outargs`` of ``[1]`` and ``inoutargs`` set to ``[2]`` can be
    called from python as::

        >>> wrapped_cfunc = cmethod(cfunc, outargs=[1], inoutargs=[2])
        >>> ret, ret_outarg, ret_inoutarg = wrapped_cfunc(inarg, inoutarg)

    Returned values will be unboxed python values unless otherwise documented
    (i.e., arrays).

    """

    # TODO: retargs...

    if cfunc is None:
        # TODO: There's probably something interesting to do in this case...
        # maybe work like a decorator if cfunc isn't given?
        return None

    if not isinstance(cfunc, CFunction):
        # Can't do argument introspection... TODO: raise an exception?
        return cfunc

    numargs = len(cfunc.args) - len(outargs)

    outargs =  [outarg(i).outtype('o') for i in outargs]
    outargs += (outarg(i).outtype('x') for i in inoutargs)
    outargs += (outarg(i).outtype('a') for i in arrays)

    outargs.sort()

    @wraps(cfunc.cfunc)
    def wrapper(*args):
        if defaults and len(args) < numargs <= (len(args) + len(defaults)):
            args += tuple(defaults[-(numargs - len(args)):])

        if len(args) != numargs:
            raise TypeError('wrapped Function {0} requires exactly {1} '
                            'arguments ({2} given)'
                            .format(cfunc.cname, numargs, len(args)))

        if checkerr is None and args and hasattr(args[0], '_checkerr'):
            _checkerr = args[0]._checkerr
        else:
            _checkerr = checkerr
        retvals = cfunc(*args, outargs=outargs, retargs=retargs, checkerr=_checkerr)

        if noret:
            if isinstance(retvals, tuple) and len(retvals) > 1:  # strip off the first return value
                retvals = retvals[1:]
                if len(retvals) == 1:
                    retvals = retvals[0]
            else:
                retvals = None
        return retvals

    if doc:
        wrapper.__doc__ = doc
    return wrapper


def cstaticmethod(cfunc, **kwargs):
    ''' Shortcut for staticmethod(cmethod(cfunc, [kwargs ...])) '''
    return staticmethod(cmethod(cfunc, **kwargs))


def cproperty(fget=None, fset=None, fdel=None, doc=None, checkerr=None):
    ''' Shortcut to create ``cmethod`` wrapped ``property``\ s.

    E.g., this:

        >>> class MyCObj(CObject):
        ...     x = property(cmethod(get_x_cfunc), cmethod(set_x_cfunc))

    becomes:

        >>> class MyCObj(CObject):
        ...     x = cproperty(get_x_cfunc, set_x_cfunc)

    If you need more control of the outargs/etc of the cmethods, stick to the
    first form, or create and assign individual cmethods and put them in a
    normal property.

    '''

    return property(fget=cmethod(fget, checkerr=checkerr),
                    fset=cmethod(fset, checkerr=checkerr),
                    fdel=cmethod(fdel, checkerr=checkerr),
                    doc=doc)


class CFunction(object):
    """ Adds some low-ish-level introspection to CFFI C functions.

    Most other wrapper classes and fuctions expect API functions
    to be wrapped in a CFunction. See ``wrapall()`` below.

    * ``ffi``: The FFI object the C function is from.
    * ``cfunc``: The C function object from CFFI.

    Attributes added to instances:

    * ``cfunc``: The C function object.
    * ``ffi``: The FFI object the C function is from.
    * ``typeof``: ffi.typeof(cfunc)
    * ``cname``: From typeof.
    * ``args``: From typeof.
    * ``kind``: From typeof.
    * ``result``: From typeof.

    """

    def __init__(self, ffi, cfunc):
        self.cfunc = cfunc
        self.ffi = ffi

        self.typeof = ffi.typeof(cfunc)
        self.args = self.typeof.args
        self.cname = self.typeof.cname
        self.kind = self.typeof.kind
        self.result = self.typeof.result


    def __call__(self, *args, **kwargs):
                 #outargs=() retargs=None):
        # Most of this code has been heavily profiled with several different
        # approaches and algorithms. However, if you think of a faster/better
        # way to do this, I'm open to ideas. This code should be fairly fast
        # because it will be the primary interface to the underlying C library,
        # potentially having wrapper functions called in tight loops.

        # pypy: 1000000 loops, best of 3: 229 ns per loop

        # Actually, looking at the profiler output, by far the biggest cost is
        # in CFFI itself (specifically calls to the _optimize_charset function
        # in the compile_sre.py module) so I don't think it's worth it to
        # squeeze much more performance out of this code...
        # Update: This seems to no longer be the case in newer pypy/cffi?

        # TODO IDEA: Consider using some kind of format string(s) to specify
        # outargs, arrays, retargs, etc? This is getting complicated enough
        # that it might make things simpler for the user?
        # Maybe something like "iioxiai" where 'i' is for "in" arg, 'o' for out
        # 'x' for in/out. Could then maybe do computed args, like array lengths
        # with something like "iiox{l5}iai" where "{l5}i" means the length of
        # the 6th (0-indexed) argument. Just something to think about...

        # TODO: Also, maybe this should support some way to change the position
        # of the 'self' argument to allow for libraries which have inconsistent
        # function signatures...

        outargs = kwargs.get('outargs')
        retargs = kwargs.get('retargs')
        cargs = self.args

        # This guard is semantically useless, but is substantially faster in
        # cpython than trying to iterate over enumerate([]). (No diff in pypy)
        if args:
            for argi, arg in enumerate(args):
                arg_orig = arg
                if hasattr(arg, '_cdata') and arg._cdata is not None:
                    arg = arg._cdata

                elif arg is None:
                    if cargs[argi].kind == 'pointer':
                        arg = self.ffi.NULL
                    else:
                        arg = 0

                elif isinstance(arg, (six.text_type, six.binary_type)):
                    string = arg
                    for ptn in re.findall(r'(w?)(char.*?) *[*\[]', self.args[argi].cname):
                        if ptn[0] == 'w' and isinstance(string, six.binary_type):
                            string = string.decode()
                        elif ptn[0] == '' and isinstance(string, six.text_type):
                            string = string.encode()
                        arg = self.ffi.new('%s%s[]' % ptn, string)

                elif isinstance(arg, self.ffi.CData) and self.ffi.typeof(arg) != cargs[argi]:
                    if cargs[argi].kind == 'pointer' and cargs[argi].item == self.ffi.typeof(arg):
                        arg = self.ffi.addressof(arg)

                elif numpy and isinstance(arg, numpy.ndarray):
                    arg = nparrayptr(arg)

                elif isinstance(arg, (bytearray, array, memoryview)):
                    arg = self.ffi.from_buffer(arg)

                if cargs[argi].cname == 'void *':
                    arg = self.ffi.cast('void *', arg)

                if arg is not arg_orig:
                    args = args[:argi] + (arg,) + args[argi + 1:]

        # If this function has out or in-out pointer args, create the pointers
        # for each, and insert/replace them in the argument list before passing
        # to the underlying C function.
        retvals = False
        if outargs:
            # TODO: use retargs to determine which args should be in the
            # return and use -1 to indicate the actual return code. Also test
            # if len(retval) == 1 and return retval_t[0].
            retvals = []

            # A few optimizations because looking up local variables is much
            # faster than looking up object attributes.
            retvals_append = retvals.append
            cfunc = self.cfunc
            ffi = self.ffi

            for outarg in outargs:
                argi, inout = outarg.argi, outarg.inout
                argtype = outarg.ffitype or cargs[argi]
                if isinstance(argtype, str):
                    outarg.ffitype = argtype = ffi.typeof(argtype)
                if inout == 'o':
                    inptr = ffi.new(argtype.cname)
                    args = args[:argi] + (inptr,) + args[argi:]
                elif inout == 'x':
                    if args[argi] is False:  # Disable inout, and and like an out instead
                        inptr = ffi.new(argtype.cname)
                    else:
                        try:
                            inptr = ffi.cast(argtype, args[argi])
                        except:
                            inptr = ffi.new(argtype.cname, args[argi])
                    args = args[:argi] + (inptr,) + args[argi+1:]
                elif inout == 'a':
                    inptr = self.get_arrayptr(args[argi], ctype=argtype)
                    args = args[:argi] + (inptr,) + args[argi+1:]
                else:
                    raise NotImplementedError
                retvals_append((inptr, outarg))

        retval = self.cfunc(*args)

        if self.result.kind == 'enum':
            retval = wrapenum(retval, self.result)

        elif self.result.cname == 'char *' and retval != self.ffi.NULL:
            retval = self.ffi.string(retval)

        if retvals:
            retval = (retval,)  # Return tuples, because it's prettier :)
            for retarg, outarg in retvals:
                if outarg.inout == 'a':
                    retval += (retarg,)  # Return arrays as-is
                else:
                    if outarg.converter:
                        retarg = outarg.converter(retarg)
                    else:
                        if retarg != self.ffi.NULL:
                            retarg = retarg[0]  # unbox regular pointer

                    retval += (retarg,)

        # This is a tad slower in pypy but substantially faster in cpython than
        # checkerr = kwargs.get('checkerr'); if checkerr is not None: ...
        if 'checkerr' in kwargs and kwargs['checkerr'] is not None:
            retval = kwargs['checkerr'](self, args, retval)
        else:
            retval = self.checkerr(self, args, retval)

        return retval

    def get_arrayptr(self, array, ctype=None):
        """ Get a CFFI compatible pointer object for an array.

        Supported ``array`` types are:

        * numpy ndarrays: The pointer to the underlying array buffer is cast
          to a CFFI pointer. Value returned from __call__ will be a pointer,
          but the numpy C buffer is updated in place, so continue to use the
          numpy ndarray object.
        * CFFI CData pointers: If the user is already working with C arrays
          (i.e., ``ffi.new("int[10]"))`` these will be returned as given.
        * Python ints and longs: These will be interpretted as the length of a
          newly allocated C array. The pointer to this array will be
          returned. ``ctype`` must be provided (CFunction's __call__ method
          does this automatically).
        * Python collections: A new C array will be allocated with a length
          equal to the length of the iterable (``len()`` is called and the
          iterable is iterated over, so don't use exhaustable generators, etc).
          ``ctype`` must be provided (CFunction's __call__ method does this
          automatically).

        """

        if numpy and isinstance(array, numpy.ndarray):
            return self.ffi.cast('void *',
                                 array.__array_interface__['data'][0])
        elif isinstance(array, self.ffi.CData):
            return array
        else:
            # Assume it's an iterable or int/long. CFFI will handle the rest.
            return self.ffi.new(self.ffi.getctype(ctype.item.cname, '[]'),
                                array)

    def checkerr(self, cfunc, args, retval):
        """ Default error checker. Checks for NULL return values and raises
        NullError.

        Can be overridden by subclasses. If ``_checkerr`` returns anything
        other than ``None``, that value will be returned by the property or
        method, otherwise original return value of the C call will be returned.
        Also useful for massaging returned values.

        """

        #TODO: Maybe should generalize to "returnhandler" or something?

        ret = retval[0] if isinstance(retval, tuple) else retval

        if ret == self.ffi.NULL:
            raise NullError('NULL returned by {0} with args {1}. '
                            .format(cfunc.cname, args))
        else:
            return retval