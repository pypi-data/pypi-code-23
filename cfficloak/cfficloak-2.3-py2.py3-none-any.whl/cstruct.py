from __future__ import absolute_import
from collections import namedtuple, Iterable

import six

from .endian_conversion import EndianTranlation
from .arrays import numpy, nparray, nparrayptr
from . import wrap


class CStruct(object):
    ''' Provides introspection to an instantiation of a CFFI ``StructType``s and ``UnionType``s.

    Instances of this class are essentially struct/union wrappers.
    Field names are easily inspected and transparent conversion of data types is done
    where possible.

    Struct fields can be passed in as positional arguments or keyword
    arguments. ``TypeError`` is raised if positional arguments overlap with
    given keyword arguments.

    The module convenience function ``wrapall`` creates ``CStruct``\ s
    for each instantiated struct and union imported from the FFI.

    '''

    def __init__(self, ffi, struct):
        '''

        * ``ffi``: The FFI object.
        * ``structtype``: a CFFI StructType or a string for the type name
          (wihtout any trailing '*' or '[]').

        '''

        self.__fldnames = {}
        self.__pfields = {}  # This is used to hold python wrappers that are linked to the underlying fields cdata
        self._endian_translate = False
        self.__hton = self.__ntoh = None

        assert isinstance(struct, ffi.CData)

        self._cdata = struct
        self.__struct_type = ffi.typeof(struct)

        if self.__struct_type.kind == 'pointer':
            self.__struct_type = self.__struct_type.item

        self._ffi = ffi

        # Sometimes structtype.name starts with a '$'...?
        try:
            self._cname = self.__struct_type.cname
        except AttributeError:
            self._cname = self.__struct_type.get_c_name()

        self.__fldnames = {} if self.__struct_type.fields is None else {detail[0]: detail[1].type for detail in self.__struct_type.fields}

        # default formatters
        # these can be overridden or removed later with set_py_converter()
        for key, fieldtype in six.iteritems(self.__fldnames):
            cname = fieldtype.cname
            if cname.startswith('char') and ('[' in cname or '*' in cname):
                self.__pfields[key] = self._ffi.string  # add string output formatter

    def __dir__(self):
        """
        List the struct fields as well
        """
        return dir(type(self)) + ([key for key in self.__fldnames.keys() if not key.startswith('_')])

    def __getattr__(self, item):
        attr = None
        if item != '_CStruct__fldnames' and self.__fldnames and item in self.__fldnames:
            attr = self.__pfields.get(item, self._cdata.__getattribute__(item))
            attr = self._ntoh(item, attr)
            if not isinstance(attr, self._ffi.CData) and callable(attr):
               attr = attr(self._cdata.__getattribute__(item))
            if isinstance(attr, self._ffi.CData):
                pattr = wrap.wrap(self._ffi, attr)
                if pattr is not attr:
                    self.__pfields[item] = pattr
                    attr = pattr
        else:
            attr = super(CStruct, self).__getattribute__(item)
            attr = self._ntoh(item, attr)
        return attr

    def __setattr__(self, key, value):
        if key != '_CStruct__fldnames' and self.__fldnames and key in self.__fldnames:
            value = self._hton(key, value)
            cname = self.__fldnames[key].cname
            if 'char' in cname and ('[' in cname or '*' in cname):
                if numpy and isinstance(value, (numpy.ndarray, nparray)):
                    self.__pfields[key] = value
                    value = nparrayptr(value)
                elif isinstance(value, (bytes, str)):
                    self.__pfields[key] = self._ffi.string  # add string output formatter
                    # Don't change value, setting from bytes or string are fine
            elif hasattr(value, '_cdata') and value._cdata is not None:
                value = value._cdata
            return setattr(self._cdata, key, value)
        else:
            return super(CStruct, self).__setattr__(key, value)

    def set_py_converter(self, key, fn=None):  # TODO have converters for set as well as get?
        if fn is None and key in self.__pfields:
            del self.__pfields['key']
        else:
            self.__pfields[key] = fn

    def enable_network_endian_translation(self):
        translate = EndianTranlation()
        translate.loadendian_translate(self._ffi)
        self.__ntoh = translate.ntoh
        self.__hton = translate.hton
        self._endian_translate = True

    def _hton(self, key, val):
        if self._endian_translate and self.__hton is not None:
            fieldtype = self.__fldnames[key].cname
            val = self.__hton[fieldtype](val) if fieldtype in self.__hton else val
        return val

    def _ntoh(self, key, val):
        if self._endian_translate and self.__ntoh is not None:
            fieldtype = self.__fldnames[key].cname
            val = self.__ntoh[fieldtype](val) if fieldtype in self.__ntoh else val
        return val

    def __str__(self):
        return "CStruct %s" % self._cname

    def __len__(self):
        return self._ffi.sizeof(self.__struct_type)

    def __eq__(self, other):
        return self is other or \
               self._cdata == other or \
               (hasattr(other, '_cdata') and self._cdata == getattr(other, '_cdata', object())) or \
               (isinstance(other, CStruct) and self.get_named_tuple() == other.get_named_tuple())

    def get_named_tuple(self):
        import warnings
        warnings.warn("deprecated", DeprecationWarning)
        return self.__as_named_tuple__()

    def __as_named_tuple__(self):
        vals = [getattr(self, field) for field in self.__fldnames]
        recurse = [f.__as_named_tuple__() if isinstance(f, CStruct) else f for f in vals]
        return namedtuple(self._cname, self.__fldnames)(*recurse)

    def __as_dict__(self):
        return self.__as_named_tuple__()._asdict()


class CStructType(object):
    ''' Provides introspection to CFFI ``StructType``s and ``UnionType``s.

    Instances have the following attributes:

    * ``ffi``: The FFI object this struct is pulled from.
    * ``cname``: The C name of the struct.
    * ``ptrname``: The C pointer type signature for this struct.
    * ``fldnames``: A list of fields this struct has.

    Instances of this class are essentially struct/union generators.
    Calling an instance of ``CStructType`` will produce a newly allocated
    struct or union.

    Struct fields can be passed in as positional arguments or keyword
    arguments. ``TypeError`` is raised if positional arguments overlap with
    given keyword arguments.

    Arrays of structs can be created with the ``array`` method.

    The module convenience function ``wrapall`` creates ``CStructType``\ s
    for each struct and union imported from the FFI.

    '''

    def __init__(self, ffi, structtype):
        '''

        * ``ffi``: The FFI object.
        * ``structtype``: a CFFI StructType or a string for the type name
          (wihtout any trailing '*' or '[]').

        '''

        self.fldnames = None
        self._cdata = None

        if isinstance(structtype, str):
            try:
                self.__struct_type = ffi.typeof(structtype.lstrip('_'))
            except AttributeError:
                self.__struct_type = ffi._parser.parse_type(structtype)

        elif isinstance(structtype, ffi.CType):
            self.__struct_type = structtype

        else:
            raise NotImplementedError("Don't know how to handle structtype of %s" % type(structtype))

        if self.__struct_type.kind == 'pointer':
            self.__struct_type = self.__struct_type.item

        self.ffi = ffi

        # Sometimes structtype.name starts with a '$'...?
        try:
            self.cname = self.__struct_type.cname
        except AttributeError:
            self.cname = self.__struct_type.get_c_name()

        self.ptrname = ffi.getctype(self.cname, '*')

        try:
            self.fldnames = None if self.__struct_type.fields is None else [detail[0] for detail in self.__struct_type.fields]
        except AttributeError:
            self.fldnames = self.__struct_type.fldnames

    def __call__(self, *args, **kwargs):
        if self.fldnames is None:
            if args or kwargs:
                raise TypeError('CStructType call with arguments on opaque '
                                'CFFI struct {0}.'.format(self.cname))
            return self.ffi.new(self.ptrname)
        else:
            if len(args) > len(self.fldnames):
                raise TypeError('CStructType got more arguments than struct '
                                'has fields. {0} > {1}'
                                .format(len(args), len(self.fldnames)))
            retval = self.ffi.new(self.ptrname)
            for fld, val in zip(self.fldnames, args):
                if fld in kwargs:
                    raise TypeError('CStructType call got multiple values for '
                                    'field name {0}'.format(fld))
                setattr(retval, fld, val)
            for fld, val in kwargs.items():
                setattr(retval, fld, val)

            return wrap.wrap(self.ffi, retval)

    def array(self, shape):
        """ Constructs a C array of the struct type with the given length.

        * ``shape``: Either an int for the length of a 1-D array, or a tuple
          for the length of each of len dimensions. I.e., [2,2] for a 2-D array
          with length 2 in each dimension. Hint: If you want an array of
          pointers just add an extra demension with length 1. I.e., [2,2,1] is
          a 2x2 array of pointers to structs.

        No explicit initialization of the elements is performed, however CFFI
        itself automatically initializes newly allocated memory to zeros.

        """

        # TODO: Factor out and integrate with carray function below?
        if isinstance(shape, Iterable):
            suffix = ('[%i]' * len(shape)) % tuple(shape)
        else:
            suffix = '[%i]' % (shape,)

        # TODO Allow passing initialization args? Maybe factor out some of the
        # code in CStructType.__call__?
        return self.ffi.new(self.ffi.getctype(self.cname + suffix))


class CUnion(CStruct):
    def __init__(self, ffi, uniontype):
        super(CUnion, self).__init__(ffi, uniontype)


class CUnionType(CStructType):
    def __init__(self, ffi, uniontype):
        super(CUnionType, self).__init__(ffi, uniontype)