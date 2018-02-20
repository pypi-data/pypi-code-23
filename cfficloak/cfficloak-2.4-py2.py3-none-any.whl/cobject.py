class CObject(object):
    ''' A pythonic representation of a C "object"

    Usually representing a set of C functions that operate over a common peice
    of data. Many C APIs have lots of functions which accept some common struct
    pointer or identifier int as the first argument being manipulated. CObject
    provides a convenient abstrtaction to making this convention more "object
    oriented". See the example below. More examples can be found in the
    cfficloak unit tests.

    Use ``cproperty`` and ``cmethod`` to wrap CFFI C functions to behave like
    instance methods, passing the instance in as the first argument. See the
    doc strings for each above.

    For C types which are not automatically coerced/converted by CFFI (such as
    C functions accepting struct pointers, etc) the subclass can set a class-
    or instance-attribute named ``_cdata`` which will be passed to the CFFI
    functions instead of ``self``. The CObject can also have a ``_cnew`` static
    method (see ``cstaticmethod``) which will be called by the base class's
    ``__init__`` and the returned value assigned to the instance's ``_cdata``.

    For example:

    libexample.h::

        typedef int point_t;
        point_t make_point(int x, int y);
        int point_x(point_t p);
        int point_y(point_t p);
        int point_setx(point_t p, int x);
        int point_sety(point_t p, int y);
        int point_move(point_t p, int x, int y);

        int point_x_abs(point_t p);
        int point_movex(point_t p, int x);

    Python usage (where ``libexample`` is an API object from
    ``ffi.verify()``)::

        >>> from cfficloak.functions import cmethod, cstaticmethod, cproperty
        >>> from cfficloak import CObject, cproperty, cstaticmethod
        >>> class Point(CObject):
        ...     x = cproperty(libexample.point_x, libexample.point_setx)
        ...     y = cproperty(libexample.point_y, libexample.point_sety)
        ...     _cnew = cstaticmethod(libexample.make_point)
        ...
        >>> p = Point(4, 2)
        >>> p.x
        4
        >>> p.x = 8
        >>> p.x
        8
        >>> p.y
        2

    You can also specify a destructor with a ``_cdel`` method in the same way
    as ``_cnew``.

    Alternatively you can assign a CFFI compatible object (either an actual
    CFFI CData object, or something CFFI automatically converts like and int)
    to the instance's _cdata attribute.

    ``cmethod`` wraps a CFunction to provide an easy way to handle 'output'
    pointer arguments, arrays, etc. (See the ``cmethod`` documentation.)::

        >>> class Point2(Point):
        ...     move = cmethod(libexample.point_move)
        ...
        >>> p2 = Point2(8, 2)
        >>> p2.move(2, 2)
        0
        >>> p2.x
        10
        >>> p2.y
        4

    If _cdata is set, attributes of the cdata object can also be retrieved from
    the CObject instance, e.g., for struct fields, etc.

    libexample cdef::

        typedef struct { int x; int y; ...; } mystruct;
        mystruct* make_mystruct(int x, int y);
        int mystruct_x(mystruct* ms);

    python::

        >>> class MyStruct(CObject):
        ...     x = cproperty(libexample.mystruct_x)
        ...     _cnew = cstaticmethod(libexample.make_mystruct)
        ...
        >>> ms = MyStruct(4, 2)
        >>> ms.x  # Call to mystruct_x via cproperty
        4
        >>> ms.y  # direct struct field access
        2

    Note: stack-passed structs are not supported yet* but pointers to
    structs work as expected if you set the ``_cdata`` attribute to the
    pointer.

    * https://bitbucket.org/cffi/cffi/issue/102


    '''

    def __init__(self, *args, **kwargs):
        if not hasattr(self, '_cdata') or self._cdata is None:
            if hasattr(self, '_cnew'):
                # C functions don't accept kwargs, so we just ignore them.
                self._cdata = self._cnew(*args)
            else:
                self._cdata = None

    def __getattr__(self, attr):
        if self._cdata is not None and hasattr(self._cdata, attr):
            return getattr(self._cdata, attr)
        else:
            raise AttributeError("{0} object has no attribute {1}"
                                 .format(repr(self.__class__), repr(attr)))

    def __del__(self):
        if hasattr(self, '_cdel'):
            self._cdel()