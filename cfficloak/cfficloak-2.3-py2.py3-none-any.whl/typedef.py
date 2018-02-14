from __future__ import absolute_import

import logging

from .cstruct import CStructType, CUnionType


class CType(object):
    """
    Provides wrapped python instance of c typedefs
    This is callable to create a new object of the type defined
    and provides functionality to easily cast objects into this type
    """
    def __init__(self, ffi, typedef):
        self.typedef = typedef
        self.ffi = ffi
        self.ctype = None
        self._cdata = None

        try:
            desc = ffi.typeof(typedef + '*').item
            if desc.kind == 'struct':
                self.ctype = CStructType(ffi, desc)
            elif desc.kind == 'union':
                self.ctype = CUnionType(ffi, desc)

        except Exception as ex:
            logging.warning(ex)

    def __repr__(self):
        return ("type: %s" % self.typedef) if not self._cdata else \
            ("%s <%s" % (self.typedef, repr(self._cdata).split(' ')[-1]))

    def __call__(self, *args, **kwargs):
        if self.ctype is None:
            raise TypeError("'%s' object is not callable", self.typedef)
        return self.ctype(*args, **kwargs)

    def cast(self, cobj):
        if self.ffi.typeof(cobj) != self.ffi.typeof(self.typedef):
            cobj = self.ffi.cast(self.typedef, cobj)
        wrapped = CType(self.ffi, self.typedef)
        setattr(wrapped, '_cdata', cobj)
        return wrapped