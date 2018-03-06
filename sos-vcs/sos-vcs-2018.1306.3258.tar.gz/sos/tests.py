#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x3601c9a0

# Compiled with Coconut version 1.3.1-post_dev25 [Dead Parrot]

# Coconut Header: -------------------------------------------------------------

import sys as _coconut_sys
from builtins import chr, filter, hex, input, int, map, object, oct, open, print, range, str, zip, filter, reversed, enumerate
py_chr, py_filter, py_hex, py_input, py_int, py_map, py_object, py_oct, py_open, py_print, py_range, py_str, py_zip, py_filter, py_reversed, py_enumerate = chr, filter, hex, input, int, map, object, oct, open, print, range, str, zip, filter, reversed, enumerate
class _coconut:
    import collections, copy, functools, imp, itertools, operator, types, weakref
    if _coconut_sys.version_info >= (3, 4):
        import asyncio
    else:
        try:
            import trollius as asyncio
        except ImportError:
            class you_need_to_install_trollius: pass
            asyncio = you_need_to_install_trollius()
    import pickle
    OrderedDict = collections.OrderedDict
    if _coconut_sys.version_info < (3, 3):
        abc = collections
    else:
        import collections.abc as abc
    Ellipsis, Exception, ImportError, IndexError, KeyError, NameError, TypeError, ValueError, StopIteration, classmethod, dict, enumerate, filter, frozenset, getattr, hasattr, hash, id, int, isinstance, issubclass, iter, len, list, map, min, max, next, object, property, range, reversed, set, slice, str, sum, super, tuple, zip, repr = Ellipsis, Exception, ImportError, IndexError, KeyError, NameError, TypeError, ValueError, StopIteration, classmethod, dict, enumerate, filter, frozenset, getattr, hasattr, hash, id, int, isinstance, issubclass, iter, len, list, map, min, max, next, object, property, range, reversed, set, slice, str, sum, super, tuple, zip, repr
def _coconut_NamedTuple(name, fields):
    return _coconut.collections.namedtuple(name, [x for x, t in fields])
class MatchError(Exception):
    """Pattern-matching error. Has attributes .pattern and .value."""
    __slots__ = ("pattern", "value")
class _coconut_tail_call:
    __slots__ = ("func", "args", "kwargs")
    def __init__(self, func, *args, **kwargs):
        self.func, self.args, self.kwargs = func, args, kwargs
_coconut_tco_func_dict = {}
def _coconut_tco(func):
    @_coconut.functools.wraps(func)
    def tail_call_optimized_func(*args, **kwargs):
        call_func = func
        while True:
            wkref = _coconut_tco_func_dict.get(_coconut.id(call_func))
            if wkref is not None and wkref() is call_func:
                call_func = call_func._coconut_tco_func
            result = call_func(*args, **kwargs)  # pass --no-tco to clean up your traceback
            if not isinstance(result, _coconut_tail_call):
                return result
            call_func, args, kwargs = result.func, result.args, result.kwargs
    tail_call_optimized_func._coconut_tco_func = func
    _coconut_tco_func_dict[_coconut.id(tail_call_optimized_func)] = _coconut.weakref.ref(tail_call_optimized_func)
    return tail_call_optimized_func
def _coconut_igetitem(iterable, index):
    if isinstance(iterable, (_coconut_reversed, _coconut_map, _coconut.filter, _coconut.zip, _coconut_enumerate, _coconut_count, _coconut.abc.Sequence)):
        return iterable[index]
    if not _coconut.isinstance(index, _coconut.slice):
        if index < 0:
            return _coconut.collections.deque(iterable, maxlen=-index)[0]
        return _coconut.next(_coconut.itertools.islice(iterable, index, index + 1))
    if index.start is not None and index.start < 0 and (index.stop is None or index.stop < 0) and index.step is None:
        queue = _coconut.collections.deque(iterable, maxlen=-index.start)
        if index.stop is not None:
            queue = _coconut.tuple(queue)[:index.stop - index.start]
        return queue
    if (index.start is not None and index.start < 0) or (index.stop is not None and index.stop < 0) or (index.step is not None and index.step < 0):
        return _coconut.tuple(iterable)[index]
    return _coconut.itertools.islice(iterable, index.start, index.stop, index.step)
class _coconut_base_compose:
    __slots__ = ("func", "funcstars")
    def __init__(self, func, *funcstars):
        self.func, self.funcstars = func, []
        for f, star in funcstars:
            if isinstance(f, _coconut_base_compose):
                self.funcstars.append((f.func, star))
                self.funcstars += f.funcstars
            else:
                self.funcstars.append((f, star))
    def __call__(self, *args, **kwargs):
        arg = self.func(*args, **kwargs)
        for f, star in self.funcstars:
            arg = f(*arg) if star else f(arg)
        return arg
    def __repr__(self):
        return _coconut.repr(self.func) + " " + " ".join(("..*> " if star else "..> ") + _coconut.repr(f) for f, star in self.funcstars)
    def __reduce__(self):
        return (self.__class__, (self.func,) + _coconut.tuple(self.funcstars))
def _coconut_forward_compose(func, *funcs): return _coconut_base_compose(func, *((f, False) for f in funcs))
def _coconut_back_compose(*funcs): return _coconut_forward_compose(*_coconut.reversed(funcs))
def _coconut_forward_star_compose(func, *funcs): return _coconut_base_compose(func, *((f, True) for f in funcs))
def _coconut_back_star_compose(*funcs): return _coconut_forward_star_compose(*_coconut.reversed(funcs))
def _coconut_pipe(x, f): return f(x)
def _coconut_star_pipe(xs, f): return f(*xs)
def _coconut_back_pipe(f, x): return f(x)
def _coconut_back_star_pipe(f, xs): return f(*xs)
def _coconut_bool_and(a, b): return a and b
def _coconut_bool_or(a, b): return a or b
def _coconut_none_coalesce(a, b): return a if a is not None else b
def _coconut_minus(a, *rest):
    if not rest:
        return -a
    for b in rest:
        a = a - b
    return a
@_coconut.functools.wraps(_coconut.itertools.tee)
def tee(iterable, n=2):
    if n >= 0 and _coconut.isinstance(iterable, (_coconut.tuple, _coconut.frozenset)):
        return (iterable,) * n
    if n > 0 and (_coconut.hasattr(iterable, "__copy__") or _coconut.isinstance(iterable, _coconut.abc.Sequence)):
        return (iterable,) + _coconut.tuple(_coconut.copy.copy(iterable) for _ in _coconut.range(n - 1))
    return _coconut.itertools.tee(iterable, n)
class reiterable:
    """Allows an iterator to be iterated over multiple times."""
    __slots__ = ("iter",)
    def __init__(self, iterable):
        self.iter = iterable
    def __iter__(self):
        self.iter, out = _coconut_tee(self.iter)
        return _coconut.iter(out)
    def __getitem__(self, index):
        return _coconut_igetitem(_coconut.iter(self), index)
    def __reversed__(self):
        return _coconut_reversed(_coconut.iter(self))
    def __len__(self):
        return _coconut.len(self.iter)
    def __repr__(self):
        return "reiterable(%r)" % (self.iter,)
    def __reduce__(self):
        return (self.__class__, (self.iter,))
    def __copy__(self):
        return self.__class__(_coconut.copy.copy(self.iter))
    def __fmap__(self, func):
        return _coconut_map(func, self)
class scan:
    """Reduce func over iterable, yielding intermediate results,
    optionally starting from initializer."""
    __slots__ = ("func", "iter", "initializer")
    empty_initializer = _coconut.object()
    def __init__(self, func, iterable, initializer=empty_initializer):
        self.func, self.iter, self.initializer = func, iterable, initializer
    def __iter__(self):
        acc = self.initializer
        if acc is not self.empty_initializer:
            yield acc
        for item in self.iter:
            if acc is self.empty_initializer:
                acc = item
            else:
                acc = self.func(acc, item)
            yield acc
    def __len__(self):
        return _coconut.len(self.iter)
    def __repr__(self):
        return "scan(%r, %r)" % (self.func, self.iter)
    def __reduce__(self):
        return (self.__class__, (self.func, self.iter))
    def __copy__(self):
        return self.__class__(self.func, _coconut.copy.copy(self.iter))
    def __fmap__(self, func):
        return _coconut_map(func, self)
class reversed:
    __slots__ = ("iter",)
    if hasattr(_coconut.map, "__doc__"):
        __doc__ = _coconut.reversed.__doc__
    def __new__(cls, iterable):
        if _coconut.isinstance(iterable, _coconut.range):
            return iterable[::-1]
        if not _coconut.hasattr(iterable, "__reversed__") or _coconut.isinstance(iterable, (_coconut.list, _coconut.tuple)):
            return _coconut.object.__new__(cls)
        return _coconut.reversed(iterable)
    def __init__(self, iterable):
        self.iter = iterable
    def __iter__(self):
        return _coconut.iter(_coconut.reversed(self.iter))
    def __getitem__(self, index):
        if _coconut.isinstance(index, _coconut.slice):
            return _coconut_igetitem(self.iter, _coconut.slice(-(index.start + 1) if index.start is not None else None, -(index.stop + 1) if index.stop else None, -(index.step if index.step is not None else 1)))
        return _coconut_igetitem(self.iter, -(index + 1))
    def __reversed__(self):
        return self.iter
    def __len__(self):
        return _coconut.len(self.iter)
    def __repr__(self):
        return "reversed(%r)" % (self.iter,)
    def __hash__(self):
        return -_coconut.hash(self.iter)
    def __reduce__(self):
        return (self.__class__, (self.iter,))
    def __copy__(self):
        return self.__class__(_coconut.copy.copy(self.iter))
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.iter == other.iter
    def __contains__(self, elem):
        return elem in self.iter
    def count(self, elem):
        """Count the number of times elem appears in the reversed iterator."""
        return self.iter.count(elem)
    def index(self, elem):
        """Find the index of elem in the reversed iterator."""
        return _coconut.len(self.iter) - self.iter.index(elem) - 1
    def __fmap__(self, func):
        return self.__class__(_coconut_map(func, self.iter))
class map(_coconut.map):
    __slots__ = ("func", "iters")
    if hasattr(_coconut.map, "__doc__"):
        __doc__ = _coconut.map.__doc__
    def __new__(cls, function, *iterables):
        new_map = _coconut.map.__new__(cls, function, *iterables)
        new_map.func, new_map.iters = function, iterables
        return new_map
    def __getitem__(self, index):
        if _coconut.isinstance(index, _coconut.slice):
            return self.__class__(self.func, *(_coconut_igetitem(i, index) for i in self.iters))
        return self.func(*(_coconut_igetitem(i, index) for i in self.iters))
    def __reversed__(self):
        return self.__class__(self.func, *(_coconut_reversed(i) for i in self.iters))
    def __len__(self):
        return _coconut.min(_coconut.len(i) for i in self.iters)
    def __repr__(self):
        return "map(%r, %s)" % (self.func, ", ".join((_coconut.repr(i) for i in self.iters)))
    def __reduce__(self):
        return (self.__class__, (self.func,) + self.iters)
    def __reduce_ex__(self, _):
        return self.__reduce__()
    def __copy__(self):
        return self.__class__(self.func, *_coconut.map(_coconut.copy.copy, self.iters))
    def __fmap__(self, func):
        return self.__class__(_coconut_forward_compose(self.func, func), *self.iters)
class parallel_map(map):
    """Multi-process implementation of map using concurrent.futures.
    Requires arguments to be pickleable."""
    __slots__ = ()
    def __iter__(self):
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor() as executor:
            return _coconut.iter(_coconut.tuple(executor.map(self.func, *self.iters)))
    def __repr__(self):
        return "parallel_" + _coconut_map.__repr__(self)
class concurrent_map(map):
    """Multi-thread implementation of map using concurrent.futures."""
    __slots__ = ()
    def __iter__(self):
        from concurrent.futures import ThreadPoolExecutor
        from multiprocessing import cpu_count  # cpu_count() * 5 is the default Python 3.5 thread count
        with ThreadPoolExecutor(cpu_count() * 5) as executor:
            return _coconut.iter(_coconut.tuple(executor.map(self.func, *self.iters)))
    def __repr__(self):
        return "concurrent_" + _coconut_map.__repr__(self)
class filter(_coconut.filter):
    __slots__ = ("func", "iter")
    if hasattr(_coconut.filter, "__doc__"):
        __doc__ = _coconut.filter.__doc__
    def __new__(cls, function, iterable):
        new_filter = _coconut.filter.__new__(cls, function, iterable)
        new_filter.func, new_filter.iter = function, iterable
        return new_filter
    def __reversed__(self):
        return self.__class__(self.func, _coconut_reversed(self.iter))
    def __repr__(self):
        return "filter(%r, %r)" % (self.func, self.iter)
    def __reduce__(self):
        return (self.__class__, (self.func, self.iter))
    def __reduce_ex__(self, _):
        return self.__reduce__()
    def __copy__(self):
        return self.__class__(self.func, _coconut.copy.copy(self.iter))
    def __fmap__(self, func):
        return _coconut_map(func, self)
class zip(_coconut.zip):
    __slots__ = ("iters",)
    if hasattr(_coconut.zip, "__doc__"):
        __doc__ = _coconut.zip.__doc__
    def __new__(cls, *iterables):
        new_zip = _coconut.zip.__new__(cls, *iterables)
        new_zip.iters = iterables
        return new_zip
    def __getitem__(self, index):
        if _coconut.isinstance(index, _coconut.slice):
            return self.__class__(*(_coconut_igetitem(i, index) for i in self.iters))
        return _coconut.tuple(_coconut_igetitem(i, index) for i in self.iters)
    def __reversed__(self):
        return self.__class__(*(_coconut_reversed(i) for i in self.iters))
    def __len__(self):
        return _coconut.min(_coconut.len(i) for i in self.iters)
    def __repr__(self):
        return "zip(%s)" % (", ".join((_coconut.repr(i) for i in self.iters)),)
    def __reduce__(self):
        return (self.__class__, self.iters)
    def __reduce_ex__(self, _):
        return self.__reduce__()
    def __copy__(self):
        return self.__class__(*_coconut.map(_coconut.copy.copy, self.iters))
    def __fmap__(self, func):
        return _coconut_map(func, self)
class enumerate(_coconut.enumerate):
    __slots__ = ("iter", "start")
    if hasattr(_coconut.enumerate, "__doc__"):
        __doc__ = _coconut.enumerate.__doc__
    def __new__(cls, iterable, start=0):
        new_enumerate = _coconut.enumerate.__new__(cls, iterable, start)
        new_enumerate.iter, new_enumerate.start = iterable, start
        return new_enumerate
    def __getitem__(self, index):
        if _coconut.isinstance(index, _coconut.slice):
            return self.__class__(_coconut_igetitem(self.iter, index), self.start + (0 if index.start is None else index.start if index.start >= 0 else len(self.iter) + index.start))
        return (self.start + index, _coconut_igetitem(self.iter, index))
    def __len__(self):
        return _coconut.len(self.iter)
    def __repr__(self):
        return "enumerate(%r, %r)" % (self.iter, self.start)
    def __reduce__(self):
        return (self.__class__, (self.iter, self.start))
    def __reduce_ex__(self, _):
        return self.__reduce__()
    def __copy__(self):
        return self.__class__(_coconut.copy.copy(self.iter), self.start)
    def __fmap__(self, func):
        return _coconut_map(func, self)
class count:
    """count(start, step) returns an infinite iterator starting at start and increasing by step."""
    __slots__ = ("start", "step")
    def __init__(self, start=0, step=1):
        self.start, self.step = start, step
    def __iter__(self):
        while True:
            yield self.start
            self.start += self.step
    def __contains__(self, elem):
        return elem >= self.start and (elem - self.start) % self.step == 0
    def __getitem__(self, index):
        if _coconut.isinstance(index, _coconut.slice) and (index.start is None or index.start >= 0) and (index.stop is None or index.stop >= 0):
            if index.stop is None:
                return self.__class__(self.start + (index.start if index.start is not None else 0), self.step * (index.step if index.step is not None else 1))
            if _coconut.isinstance(self.start, _coconut.int) and _coconut.isinstance(self.step, _coconut.int):
                return _coconut.range(self.start + self.step * (index.start if index.start is not None else 0), self.start + self.step * index.stop, self.step * (index.step if index.step is not None else 1))
            return _coconut_map(self.__getitem__, _coconut.range(index.start if index.start is not None else 0, index.stop, index.step if index.step is not None else 1))
        if index >= 0:
            return self.start + self.step * index
        raise _coconut.IndexError("count indices must be positive")
    def count(self, elem):
        """Count the number of times elem appears in the count."""
        return int(elem in self)
    def index(self, elem):
        """Find the index of elem in the count."""
        if elem not in self:
            raise _coconut.ValueError(_coconut.repr(elem) + " is not in count")
        return (elem - self.start) // self.step
    def __repr__(self):
        return "count(%r, %r)" % (self.start, self.step)
    def __hash__(self):
        return _coconut.hash((self.start, self.step))
    def __reduce__(self):
        return (self.__class__, (self.start, self.step))
    def __copy__(self):
        return self.__class__(self.start, self.step)
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.start == other.start and self.step == other.step
    def __fmap__(self, func):
        return _coconut_map(func, self)
class groupsof:
    """groupsof(n, iterable) splits iterable into groups of size n.
    If the length of the iterable is not divisible by n, the last group may be of size < n."""
    __slots__ = ("group_size", "iter")
    def __init__(self, n, iterable):
        self.iter = iterable
        try:
            self.group_size = _coconut.int(n)
        except _coconut.ValueError:
            raise _coconut.TypeError("group size must be an int; not %r" % (n,))
        if self.group_size <= 0:
            raise _coconut.ValueError("group size must be > 0; not %r" % (self.group_size,))
    def __iter__(self):
        loop, iterator = True, _coconut.iter(self.iter)
        while loop:
            group = []
            for _ in _coconut.range(self.group_size):
                try:
                    group.append(_coconut.next(iterator))
                except _coconut.StopIteration:
                    loop = False
                    break
            if group:
                yield _coconut.tuple(group)
    def __len__(self):
        return _coconut.len(self.iter)
    def __repr__(self):
        return "groupsof(%r)" % (self.iter,)
    def __reduce__(self):
        return (self.__class__, (self.group_size, self.iter))
    def __copy__(self):
        return self.__class__(self.group_size, _coconut.copy.copy(self.iter))
    def __fmap__(self, func):
        return _coconut_map(func, self)
def recursive_iterator(func):
    """Decorator that optimizes a function for iterator recursion."""
    tee_store, backup_tee_store = {}, []
    @_coconut.functools.wraps(func)
    def recursive_iterator_func(*args, **kwargs):
        key, use_backup = (args, _coconut.frozenset(kwargs)), False
        try:
            hash(key)
        except _coconut.Exception:
            try:
                key = _coconut.pickle.dumps(key, -1)
            except _coconut.Exception:
                use_backup = True
        if use_backup:
            for i, (k, v) in _coconut.enumerate(backup_tee_store):
                if k == key:
                    to_tee, store_pos = v, i
                    break
            else:  # no break
                to_tee, store_pos = func(*args, **kwargs), None
            to_store, to_return = _coconut_tee(to_tee)
            if store_pos is None:
                backup_tee_store.append([key, to_store])
            else:
                backup_tee_store[store_pos][1] = to_store
        else:
            tee_store[key], to_return = _coconut_tee(tee_store.get(key) or func(*args, **kwargs))
        return to_return
    return recursive_iterator_func
def addpattern(base_func):
    """Decorator to add a new case to a pattern-matching function,
    where the new case is checked last."""
    def pattern_adder(func):
        @_coconut_tco
        @_coconut.functools.wraps(func)
        def add_pattern_func(*args, **kwargs):
            try:
                return base_func(*args, **kwargs)
            except _coconut_MatchError:
                return _coconut_tail_call(func, *args, **kwargs)
        return add_pattern_func
    return pattern_adder
def prepattern(base_func):
    """DEPRECATED: Use addpattern instead."""
    def pattern_prepender(func):
        return addpattern(func)(base_func)
    return pattern_prepender
class _coconut_partial:
    __slots__ = ("func", "_argdict", "_arglen", "_stargs", "keywords")
    if hasattr(_coconut.functools.partial, "__doc__"):
        __doc__ = _coconut.functools.partial.__doc__
    def __init__(self, func, argdict, arglen, *args, **kwargs):
        self.func, self._argdict, self._arglen, self._stargs, self.keywords = func, argdict, arglen, args, kwargs
    def __reduce__(self):
        return (self.__class__, (self.func, self._argdict, self._arglen) + self._stargs, self.keywords)
    def __setstate__(self, keywords):
        self.keywords = keywords
    @property
    def args(self):
        return _coconut.tuple(self._argdict.get(i) for i in _coconut.range(self._arglen)) + self._stargs
    def __call__(self, *args, **kwargs):
        callargs = []
        argind = 0
        for i in _coconut.range(self._arglen):
            if i in self._argdict:
                callargs.append(self._argdict[i])
            elif argind >= _coconut.len(args):
                raise _coconut.TypeError("expected at least " + _coconut.str(self._arglen - _coconut.len(self._argdict)) + " argument(s) to " + _coconut.repr(self))
            else:
                callargs.append(args[argind])
                argind += 1
        callargs += self._stargs
        callargs += args[argind:]
        kwargs.update(self.keywords)
        return self.func(*callargs, **kwargs)
    def __repr__(self):
        args = []
        for i in _coconut.range(self._arglen):
            if i in self._argdict:
                args.append(_coconut.repr(self._argdict[i]))
            else:
                args.append("?")
        for arg in self._stargs:
            args.append(_coconut.repr(arg))
        return _coconut.repr(self.func) + "$(" + ", ".join(args) + ")"
def makedata(data_type, *args, **kwargs):
    """Call the original constructor of the given data type or class with the given arguments."""
    if _coconut.hasattr(data_type, "_make") and (_coconut.issubclass(data_type, _coconut.tuple) or _coconut.isinstance(data_type, _coconut.tuple)):
        return data_type._make(args, **kwargs)
    return _coconut.super(data_type, data_type).__new__(data_type, *args, **kwargs)
def datamaker(data_type):
    """DEPRECATED: Use makedata instead."""
    return _coconut.functools.partial(makedata, data_type)
def consume(iterable, keep_last=0):
    """consume(iterable, keep_last) fully exhausts iterable and return the last keep_last elements."""
    return _coconut.collections.deque(iterable, maxlen=keep_last)  # fastest way to exhaust an iterator
class starmap(_coconut.itertools.starmap):
    __slots__ = ("func", "iter")
    if hasattr(_coconut.itertools.starmap, "__doc__"):
        __doc__ = _coconut.itertools.starmap.__doc__
    def __new__(cls, function, iterable):
        new_map = _coconut.itertools.starmap.__new__(cls, function, iterable)
        new_map.func, new_map.iter = function, iterable
        return new_map
    def __getitem__(self, index):
        if _coconut.isinstance(index, _coconut.slice):
            return self.__class__(self.func, _coconut_igetitem(self.iter, index))
        return self.func(*_coconut_igetitem(self.iter, index))
    def __reversed__(self):
        return self.__class__(self.func, *_coconut_reversed(self.iter))
    def __len__(self):
        return _coconut.len(self.iter)
    def __repr__(self):
        return "starmap(%r, %r)" % (self.func, self.iter)
    def __reduce__(self):
        return (self.__class__, (self.func, self.iter))
    def __reduce_ex__(self, _):
        return self.__reduce__()
    def __copy__(self):
        return self.__class__(self.func, _coconut.copy.copy(self.iter))
    def __fmap__(self, func):
        return self.__class__(_coconut_forward_compose(self.func, func), self.iter)
def fmap(func, obj):
    """fmap(func, obj) creates a copy of obj with func applied to its contents.
    Override by defining .__fmap__(func)."""
    if _coconut.hasattr(obj, "__fmap__"):
        return obj.__fmap__(func)
    args = _coconut_starmap(func, obj.items()) if _coconut.isinstance(obj, _coconut.abc.Mapping) else _coconut_map(func, obj)
    if _coconut.isinstance(obj, _coconut.tuple) and _coconut.hasattr(obj, "_make"):
        return obj._make(args)
    if _coconut.isinstance(obj, (_coconut.map, _coconut.range, _coconut.abc.Iterator)):
        return args
    if _coconut.isinstance(obj, _coconut.str):
        return "".join(args)
    return obj.__class__(args)
def memoize(maxsize=None, *args, **kwargs):
    """Decorator that memoizes a function,
    preventing it from being recomputed if it is called multiple times with the same arguments."""
    return _coconut.functools.lru_cache(maxsize, *args, **kwargs)
_coconut_MatchError, _coconut_count, _coconut_enumerate, _coconut_reversed, _coconut_map, _coconut_starmap, _coconut_tee, _coconut_zip, TYPE_CHECKING, reduce, takewhile, dropwhile = MatchError, count, enumerate, reversed, map, starmap, tee, zip, False, _coconut.functools.reduce, _coconut.itertools.takewhile, _coconut.itertools.dropwhile

# Compiled Coconut: -----------------------------------------------------------

# Copyright Arne Bachmann
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

import codecs
import enum
import json
import logging
import os
import shutil
sys = _coconut_sys
import time
import traceback
import unittest
import uuid
from io import BytesIO
from io import BufferedRandom
from io import TextIOWrapper

try:
    if TYPE_CHECKING:  # true only during compilation/mypy run
        from typing import *
        mock = None  # type: Any  # to avoid mypy complaint
except:
    pass

try:  # Python 3
    from unittest import mock  # Python 3
except:  # installed via pip
    import mock  # installed via pip

testFolder = os.path.abspath(os.path.join(os.getcwd(), "test"))  # this needs to be set before the configr and sos imports
os.environ["TEST"] = testFolder  # needed to mock configr library calls in sos

import configr
import sos  # import of package, not file

sos.defaults["defaultbranch"] = "trunk"  # because sos.main() is never called
sos.defaults["useChangesCommand"] = True  # because sos.main() is never called
sos.defaults["useUnicodeFont"] = False  # because sos.main() is never called


def determineFilesystemTimeResolution() -> 'float':
    name = str(uuid.uuid4())  # type: str
    with open(name, "w") as fd:  # create temporary file
        fd.write("x")  # create temporary file
    mt = os.stat(sos.encode(name)).st_mtime  # type: float  # get current timestamp
    while os.stat(sos.encode(name)).st_mtime == mt:  # wait until timestamp modified
        time.sleep(0.05)  # to avoid 0.00s bugs (came up some time for unknown reasons)
        with open(name, "w") as fd:
            fd.write("x")
    mt, start, _count = os.stat(sos.encode(name)).st_mtime, time.time(), 0
    while os.stat(sos.encode(name)).st_mtime == mt:  # now cound and measure time until modified again
        time.sleep(0.05)
        _count += 1
        with open(name, "w") as fd:
            fd.write("x")
    os.unlink(name)
    fsprecision = round(time.time() - start, 2)  # type: float
    print("File system timestamp precision is %s%.2fs; wrote to the file %d times during that time" % ("probably even higher than " if fsprecision == 0.05 else "", fsprecision, _count))
    return fsprecision


FS_PRECISION = determineFilesystemTimeResolution() * 1.55

def sync():
    try:  # only Linux  if sys.version_info[:2] >= (3, 3):
        os.sync()  # only Linux  if sys.version_info[:2] >= (3, 3):
    except:  # Windows testing on AppVeyor
        time.sleep(FS_PRECISION)  # Windows testing on AppVeyor


@_coconut_tco
def debugTestRunner(post_mortem=None):
    ''' Unittest runner doing post mortem debugging on failing tests. '''
    import pdb
    if post_mortem is None:
        post_mortem = pdb.post_mortem
    class DebugTestResult(unittest.TextTestResult):
        def addError(_, test, err):  # called before tearDown()
            traceback.print_exception(*err)
            post_mortem(err[2])
            super(DebugTestResult, _).addError(test, err)
        def addFailure(_, test, err):
            traceback.print_exception(*err)
            post_mortem(err[2])
            super(DebugTestResult, _).addFailure(test, err)
    return _coconut_tail_call(unittest.TextTestRunner, resultclass=DebugTestResult)

@_coconut_tco
def wrapChannels(func: '_coconut.typing.Callable[..., Any]') -> 'str':
    ''' Wrap function call to capture and return strings emitted on stdout and stderr. '''
    oldv = sys.argv
    buf = TextIOWrapper(BufferedRandom(BytesIO(b"")), encoding=sos.UTF8)
    handler = logging.StreamHandler(buf)  # TODO doesn't seem to be captured
    sys.stdout = sys.stderr = buf
    logging.getLogger().addHandler(handler)
    try:  # capture output into buf
        func()  # capture output into buf
    except Exception as E:
        buf.write(str(E) + "\n")
        traceback.print_exc(file=buf)
    except SystemExit as F:
        buf.write("EXIT CODE %s" % F.code + "\n")
        traceback.print_exc(file=buf)
    logging.getLogger().removeHandler(handler)
    sys.argv, sys.stdout, sys.stderr = oldv, sys.__stdout__, sys.__stderr__  # TODO when run using pythonw.exe and/or no console, these could be None
    buf.seek(0)
    return _coconut_tail_call(buf.read)

def mockInput(datas: '_coconut.typing.Sequence[str]', func: '_coconut.typing.Callable[..., Any]') -> 'Any':
    if sos.coco_version < (1, 3, 1, 21):
        import builtins
        with mock.patch("builtins.input", side_effect=datas):
            return func()
    else:
        try:  # via python sos/tests.py
            with mock.patch("sos._utility.input", side_effect=datas):
                return func()
        except:  # via setup.py
            with mock.patch("sos.utility.input", side_effect=datas):
                return func()

def setRepoFlag(name: 'str', value: 'bool'):
    with open(sos.metaFolder + os.sep + sos.metaFile, "r") as fd:
        flags, branches, config = json.loads(fd.read())
    flags[name] = value
    with open(sos.metaFolder + os.sep + sos.metaFile, "w") as fd:
        fd.write(json.dumps((flags, branches, config)))

def checkRepoFlag(name: 'str', flag: '_coconut.typing.Optional[bool]'=None, value: '_coconut.typing.Optional[Any]'=None) -> 'bool':
    with open(sos.metaFolder + os.sep + sos.metaFile, "r") as fd:
        flags, branches, config = json.loads(fd.read())
    return (name in flags and flags[name] == flag) if flag is not None else (name in config and config[name] == value)


class Tests(unittest.TestCase):
    ''' Entire test suite. '''

    def setUp(_):
        sos.Metadata.singleton = None
        for entry in os.listdir(testFolder):  # cannot remove testFolder on Windows when using TortoiseSVN as VCS
            resource = os.path.join(testFolder, entry)
            shutil.rmtree(sos.encode(resource)) if os.path.isdir(sos.encode(resource)) else os.unlink(sos.encode(resource))
        os.chdir(testFolder)


    def assertAllIn(_, what: '_coconut.typing.Sequence[str]', where: 'Union[str, List[str]]', only: 'bool'=False):
        for w in what:
            _.assertIn(w, where)
        if only:
            _.assertEqual(len(what), len(where))

    def assertAllNotIn(_, what: '_coconut.typing.Sequence[str]', where: 'Union[str, List[str]]'):
        for w in what:
            _.assertNotIn(w, where)

    def assertInAll(_, what: 'str', where: '_coconut.typing.Sequence[str]'):
        for w in where:
            _.assertIn(what, w)

    def assertInAny(_, what: 'str', where: '_coconut.typing.Sequence[str]'):
        _.assertTrue(any((what in w for w in where)))

    def assertNotInAny(_, what: 'str', where: '_coconut.typing.Sequence[str]'):
        _.assertFalse(any((what in w for w in where)))

    def createFile(_, number: 'Union[int, str]', contents: 'str'="x" * 10, prefix: '_coconut.typing.Optional[str]'=None):
        if prefix and not os.path.exists(prefix):
            os.makedirs(prefix)
        with open(("." if prefix is None else prefix) + os.sep + (("file%d" % number) if isinstance(number, int) else number), "wb") as fd:
            fd.write(contents if isinstance(contents, bytes) else contents.encode("cp1252"))
        sync()

    def existsFile(_, number: 'Union[int, str]', expectedContents: 'bytes'=None) -> 'bool':
        sync()
        if not os.path.exists(("." + os.sep + "file%d" % number) if isinstance(number, int) else number):
            return False
        if expectedContents is None:
            return True
        with open(("." + os.sep + "file%d" % number) if isinstance(number, int) else number, "rb") as fd:
            return fd.read() == expectedContents

    def testAccessor(_):
        a = sos.Accessor({"a": 1})
        _.assertEqual((1, 1), (a["a"], a.a))

    def testRestoreFile(_):
        m = sos.Metadata()
        os.makedirs(sos.revisionFolder(0, 0))
        _.createFile("hashed_file", "content", sos.revisionFolder(0, 0))
        m.restoreFile(relPath="restored", branch=0, revision=0, pinfo=sos.PathInfo("hashed_file", 0, (time.time() - 2000) * 1000, "content hash"))
        _.assertTrue(_.existsFile("restored", b""))

    def testGetAnyOfmap(_):
        _.assertEqual(2, sos.getAnyOfMap({"a": 1, "b": 2}, ["x", "b"]))
        _.assertIsNone(sos.getAnyOfMap({"a": 1, "b": 2}, []))

    def testAjoin(_):
        _.assertEqual("a1a2", sos.ajoin("a", ["1", "2"]))
        _.assertEqual("* a\n* b", sos.ajoin("* ", ["a", "b"], "\n"))

    def testFindChanges(_):
        m = sos.Metadata(os.getcwd())
        try:
            sos.config(["set", "texttype", "*"])
        except SystemExit as E:
            _.assertEqual(0, E.code)
        try:  # will be stripped from leading paths anyway
            sos.config(["set", "ignores", "test/*.cfg;D:\\apps\\*.cfg.bak"])  # will be stripped from leading paths anyway
        except SystemExit as E:
            _.assertEqual(0, E.code)
        m = sos.Metadata(os.getcwd())  # reload from file system
        for file in [f for f in os.listdir() if f.endswith(".bak")]:  # remove configuration file
            os.unlink(file)  # remove configuration file
        _.createFile(1, "1")
        m.createBranch(0)
        _.assertEqual(1, len(m.paths))
        time.sleep(FS_PRECISION)  # time required by filesystem time resolution issues
        _.createFile(1, "2")  # modify existing file
        _.createFile(2, "2")  # add another file
        m.loadCommit(0, 0)
        changes, msg = m.findChanges()  # detect time skew
        _.assertEqual(1, len(changes.additions))
        _.assertEqual(0, len(changes.deletions))
        _.assertEqual(1, len(changes.modifications))
        _.assertEqual(0, len(changes.moves))
        m.paths.update(changes.additions)
        m.paths.update(changes.modifications)
        _.createFile(2, "12")  # modify file again
        changes, msg = m.findChanges(0, 1)  # by size, creating new commit
        _.assertEqual(0, len(changes.additions))
        _.assertEqual(0, len(changes.deletions))
        _.assertEqual(1, len(changes.modifications))
        _.assertEqual(0, len(changes.moves))
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 1)))
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2")))
# TODO test moves

    def testMoves(_):
        _.createFile(1, "1")
        _.createFile(2, "2", "sub")
        sos.offline(options=["--strict", "--compress"])  # TODO move compress flag to own test function and check if it actually works
        os.renames(sos.encode("." + os.sep + "file1"), sos.encode("sub" + os.sep + "file1"))
        os.renames(sos.encode("sub" + os.sep + "file2"), sos.encode("." + os.sep + "file2"))
        out = wrapChannels(lambda: sos.changes())  # type: str
        _.assertIn("MOV ./file2  <-  sub/file2", out)
        _.assertIn("MOV sub/file1  <-  ./file1", out)
        out = wrapChannels(lambda: sos.commit())
        _.assertIn("MOV ./file2  <-  sub/file2", out)
        _.assertIn("MOV sub/file1  <-  ./file1", out)
        _.assertIn("Created new revision r01 (+00/-00/~00/#02)", out)  # TODO why is this not captured?

    def testPatternPaths(_):
        sos.offline(options=["--track"])
        os.mkdir("sub")
        _.createFile("sub" + os.sep + "file1", "sdfsdf")
        sos.add("sub", "sub/file?")
        sos.commit("test")  # should pick up sub/file1 pattern
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # sub/file1 was added
        _.createFile(1)
        try:  # should not commit anything, as the file in base folder doesn't match the tracked pattern
            sos.commit("nothing")  # should not commit anything, as the file in base folder doesn't match the tracked pattern
            _.fail()  # should not commit anything, as the file in base folder doesn't match the tracked pattern
        except:
            pass

    def testNoArgs(_):
        pass  # call "sos" without arguments should simply show help or info about missing arguments

    def testAutoUpgrade(_):
        sos.offline()
        with codecs.open(sos.encode(os.path.join(sos.metaFolder, sos.metaFile)), "r", encoding=sos.UTF8) as fd:
            repo, branches, config = json.load(fd)
        repo["version"] = None  # lower than any pip version
        branches[:] = [branch[:5] for branch in branches]  # simulate some older state
        del repo["format"]  # simulate pre-1.3.5
        with codecs.open(sos.encode(os.path.join(sos.metaFolder, sos.metaFile)), "w", encoding=sos.UTF8) as fd:
            json.dump((repo, branches, config), fd, ensure_ascii=False)
        out = wrapChannels(lambda: sos.status(options=["--repo"]))
        _.assertAllIn(["pre-1.2", "Upgraded repository metadata to match SOS version '2018.1210.3028'", "Upgraded repository metadata to match SOS version '1.3.5'"], out)

    def testFastBranching(_):
        _.createFile(1)
        sos.offline(options=["--strict"])  # b0/r0 = ./file1
        _.createFile(2)
        os.unlink("file1")
        sos.commit()  # b0/r1 = ./file2
        sos.branch(options=["--fast", "--last"])  # branch b1 from b0/1 TODO modify once --fast becomes the new normal
        _.assertAllIn([sos.metaFile, sos.metaBack, "b0", "b1"], os.listdir(sos.metaFolder), only=True)
        _.createFile(3)
        sos.commit()  # b1/r2 = ./file2, ./file3
        _.assertAllIn([sos.metaFile, "r2"], os.listdir(sos.branchFolder(1)), only=True)
        sos.branch(options=["--fast", "--last"])  # branch b2 from b1/2
        sos.destroy("0")  # remove parent of b1 and transitive parent of b2
        _.assertAllIn([sos.metaFile, sos.metaBack, "b0_last", "b1", "b2"], os.listdir(sos.metaFolder), only=True)  # branch 0 was removed
        _.assertAllIn([sos.metaFile, "r0", "r1", "r2"], os.listdir(sos.branchFolder(1)), only=True)  # revisions were copied to branch 1
        _.assertAllIn([sos.metaFile, "r0", "r1", "r2"], os.listdir(sos.branchFolder(2)), only=True)  # revisions were copied to branch 1
# TODO test also other functions like status --repo, log

    def testModificationWithOldRevisionRecognition(_):
        now = time.time()  # type: float
        _.createFile(1)
        sync()
        sos.offline(options=["--strict"])
        _.createFile(1, "abc")  # modify contents
        os.utime(sos.encode("file1"), (now - 2000, now - 2000))  # make it look like an older version
        sync()
        out = wrapChannels(lambda: sos.changes())
        _.assertAllIn(["<older than last revision>", "<older than previously committed>"], out)
        out = wrapChannels(lambda: sos.commit())
        _.assertAllIn(["<older than last revision>", "<older than previously committed>"], out)

    def testGetParentBranch(_):
        m = sos.Accessor({"branches": {0: sos.Accessor({"parent": None, "revision": None}), 1: sos.Accessor({"parent": 0, "revision": 1})}})
        _.assertEqual(0, sos.Metadata.getParentBranch(m, 1, 0))
        _.assertEqual(0, sos.Metadata.getParentBranch(m, 1, 1))
        _.assertEqual(1, sos.Metadata.getParentBranch(m, 1, 2))
        _.assertEqual(0, sos.Metadata.getParentBranch(m, 0, 10))

    def testTokenizeGlobPattern(_):
        _.assertEqual([], sos.tokenizeGlobPattern(""))
        _.assertEqual([sos.GlobBlock(False, "*", 0)], sos.tokenizeGlobPattern("*"))
        _.assertEqual([sos.GlobBlock(False, "*", 0), sos.GlobBlock(False, "???", 1)], sos.tokenizeGlobPattern("*???"))
        _.assertEqual([sos.GlobBlock(True, "x", 0), sos.GlobBlock(False, "*", 1), sos.GlobBlock(True, "x", 2)], sos.tokenizeGlobPattern("x*x"))
        _.assertEqual([sos.GlobBlock(True, "x", 0), sos.GlobBlock(False, "*", 1), sos.GlobBlock(False, "??", 2), sos.GlobBlock(False, "*", 4), sos.GlobBlock(True, "x", 5)], sos.tokenizeGlobPattern("x*??*x"))
        _.assertEqual([sos.GlobBlock(False, "?", 0), sos.GlobBlock(True, "abc", 1), sos.GlobBlock(False, "*", 4)], sos.tokenizeGlobPattern("?abc*"))

    def testTokenizeGlobPatterns(_):
        try:  # because number of literal strings differs
            sos.tokenizeGlobPatterns("x*x", "x*")  # because number of literal strings differs
            _.fail()  # because number of literal strings differs
        except:
            pass
        try:  # because glob patterns differ
            sos.tokenizeGlobPatterns("x*", "x?")  # because glob patterns differ
            _.fail()  # because glob patterns differ
        except:
            pass
        try:  # glob patterns differ, regardless of position
            sos.tokenizeGlobPatterns("x*", "?x")  # glob patterns differ, regardless of position
            _.fail()  # glob patterns differ, regardless of position
        except:
            pass
        sos.tokenizeGlobPatterns("x*", "*x")  # succeeds, because glob patterns match (differ only in position)
        sos.tokenizeGlobPatterns("*xb?c", "*x?bc")  # succeeds, because glob patterns match (differ only in position)
        try:  # succeeds, because glob patterns match (differ only in position)
            sos.tokenizeGlobPatterns("a???b*", "ab???*")  # succeeds, because glob patterns match (differ only in position)
            _.fail()  # succeeds, because glob patterns match (differ only in position)
        except:
            pass

    def testConvertGlobFiles(_):
        _.assertEqual(["xxayb", "aacb"], [r[1] for r in sos.convertGlobFiles(["axxby", "aabc"], *sos.tokenizeGlobPatterns("a*b?", "*a?b"))])
        _.assertEqual(["1qq2ww3", "1abcbx2xbabc3"], [r[1] for r in sos.convertGlobFiles(["qqxbww", "abcbxxbxbabc"], *sos.tokenizeGlobPatterns("*xb*", "1*2*3"))])

    def testFolderRemove(_):
        m = sos.Metadata(os.getcwd())
        _.createFile(1)
        _.createFile("a", prefix="sub")
        sos.offline()
        _.createFile(2)
        os.unlink("sub" + os.sep + "a")
        os.rmdir("sub")
        changes = sos.changes()  # TODO replace by output check
        _.assertEqual(1, len(changes.additions))
        _.assertEqual(0, len(changes.modifications))
        _.assertEqual(1, len(changes.deletions))
        _.createFile("a", prefix="sub")
        changes = sos.changes()
        _.assertEqual(0, len(changes.deletions))

    def testSwitchConflict(_):
        sos.offline(options=["--strict"])  # (r0)
        _.createFile(1)
        sos.commit()  # add file (r1)
        os.unlink("file1")
        sos.commit()  # remove (r2)
        _.createFile(1, "something else")
        sos.commit()  # (r3)
        sos.switch("/1")  # updates file1 - marked as MOD, because mtime was changed
        _.existsFile(1, "x" * 10)
        sos.switch("/2", ["--force"])  # remove file1 requires --force, because size/content (or mtime in non-strict mode) is different to head of branch
        sos.switch("/0")  # do nothing, as file1 is already removed
        sos.switch("/1")  # add file1 back
        sos.switch("/", ["--force"])  # requires force because changed vs. head of branch
        _.existsFile(1, "something else")

    def testComputeSequentialPathSet(_):
        os.makedirs(sos.revisionFolder(0, 0))
        os.makedirs(sos.revisionFolder(0, 1))
        os.makedirs(sos.revisionFolder(0, 2))
        os.makedirs(sos.revisionFolder(0, 3))
        os.makedirs(sos.revisionFolder(0, 4))
        m = sos.Metadata(os.getcwd())
        m.branch = 0
        m.commit = 2
        m.saveBranches()
        m.paths = {"./a": sos.PathInfo("", 0, 0, "")}
        m.saveCommit(0, 0)  # initial
        m.paths["./a"] = sos.PathInfo("", 1, 0, "")
        m.saveCommit(0, 1)  # mod
        m.paths["./b"] = sos.PathInfo("", 0, 0, "")
        m.saveCommit(0, 2)  # add
        m.paths["./a"] = sos.PathInfo("", None, 0, "")
        m.saveCommit(0, 3)  # del
        m.paths["./a"] = sos.PathInfo("", 2, 0, "")
        m.saveCommit(0, 4)  # readd
        m.commits = {i: sos.CommitInfo(i, 0, None) for i in range(5)}
        m.saveBranch(0)
        m.branches = {0: sos.BranchInfo(0, 0), 1: sos.BranchInfo(1, 0)}
        m.saveBranches()
        m.computeSequentialPathSet(0, 4)
        _.assertEqual(2, len(m.paths))

    def testParseRevisionString(_):
        m = sos.Metadata(os.getcwd())
        m.branch = 1
        m.commits = {0: 0, 1: 1, 2: 2}
        _.assertEqual((1, 3), m.parseRevisionString("3"))
        _.assertEqual((2, 3), m.parseRevisionString("2/3"))
        _.assertEqual((1, -1), m.parseRevisionString(None))
        _.assertEqual((1, -1), m.parseRevisionString(""))
        _.assertEqual((2, -1), m.parseRevisionString("2/"))
        _.assertEqual((1, -2), m.parseRevisionString("/-2"))
        _.assertEqual((1, -1), m.parseRevisionString("/"))

    def testOfflineEmpty(_):
        os.mkdir("." + os.sep + sos.metaFolder)
        try:
            sos.offline("trunk")
            _.fail()
        except SystemExit as E:
            _.assertEqual(1, E.code)
        os.rmdir("." + os.sep + sos.metaFolder)
        sos.offline("test")
        _.assertIn(sos.metaFolder, os.listdir("."))
        _.assertAllIn(["b0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))
        _.assertAllIn(["r0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # only branch folder and meta data file
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0")))  # only commit folder and meta data file
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 0))))  # only meta data file

    def testOfflineWithFiles(_):
        _.createFile(1, "x" * 100)
        _.createFile(2)
        sos.offline("test")
        _.assertAllIn(["file1", "file2", sos.metaFolder], os.listdir("."))
        _.assertAllIn(["b0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))
        _.assertAllIn(["r0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))
        _.assertAllIn([sos.metaFile, "03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2", "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0" + os.sep + "r0"))
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # only branch folder and meta data file
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0")))  # only commit folder and meta data file
        _.assertEqual(3, len(os.listdir(sos.revisionFolder(0, 0))))  # only meta data file plus branch base file copies

    def testBranch(_):
        _.createFile(1, "x" * 100)
        _.createFile(2)
        sos.offline("test")  # b0/r0
        sos.branch("other")  # b1/r0
        _.assertAllIn(["b0", "b1", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))
        _.assertEqual(list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))), list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b1"))))
        _.assertEqual(list(sorted(os.listdir(sos.revisionFolder(0, 0)))), list(sorted(os.listdir(sos.revisionFolder(1, 0)))))
        _.createFile(1, "z")  # modify file
        sos.branch()  # b2/r0  branch to unnamed branch with modified file tree contents
        _.assertNotEqual(os.stat(sos.encode("." + os.sep + sos.metaFolder + os.sep + "b1" + os.sep + "r0" + os.sep + "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa")).st_size, os.stat(sos.encode("." + os.sep + sos.metaFolder + os.sep + "b2" + os.sep + "r0" + os.sep + "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa")).st_size)
        _.createFile(3, "z")
        sos.branch("from_last_revision", options=["--last", "--stay"])  # b3/r0 create copy of other file1,file2 and don't switch
        _.assertEqual(list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b3" + os.sep + "r0"))), list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b2" + os.sep + "r0"))))
# Check sos.status output which branch is marked


    def testComittingAndChanges(_):
        _.createFile(1, "x" * 100)
        _.createFile(2)
        sos.offline("test")
        changes = sos.changes()
        _.assertEqual(0, len(changes.additions))
        _.assertEqual(0, len(changes.deletions))
        _.assertEqual(0, len(changes.modifications))
        _.createFile(1, "z")  # size change
        changes = sos.changes()
        _.assertEqual(0, len(changes.additions))
        _.assertEqual(0, len(changes.deletions))
        _.assertEqual(1, len(changes.modifications))
        sos.commit("message")
        _.assertAllIn(["r0", "r1", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))
        _.assertAllIn([sos.metaFile, "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"], os.listdir(sos.revisionFolder(0, 1)))
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # no further files, only the modified one
        _.assertEqual(1, len(sos.changes("/0").modifications))  # vs. explicit revision on current branch
        _.assertEqual(1, len(sos.changes("0/0").modifications))  # vs. explicit branch/revision
        _.createFile(1, "")  # modify to empty file, mentioned in meta data, but not stored as own file
        os.unlink("file2")
        changes = sos.changes()
        _.assertEqual(0, len(changes.additions))
        _.assertEqual(1, len(changes.deletions))
        _.assertEqual(1, len(changes.modifications))
        sos.commit("modified")
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 2))))  # no additional files, only mentions in metadata
        try:  # expecting Exit due to no changes
            sos.commit("nothing")  # expecting Exit due to no changes
            _.fail()  # expecting Exit due to no changes
        except:
            pass

    def testGetBranch(_):
        m = sos.Metadata(os.getcwd())
        m.branch = 1  # current branch
        m.branches = {0: sos.BranchInfo(0, 0, "trunk")}
        _.assertEqual(27, m.getBranchByName(27))
        _.assertEqual(0, m.getBranchByName("trunk"))
        _.assertEqual(1, m.getBranchByName(""))  # split from "/"
        _.assertIsNone(m.getBranchByName("unknown"))
        m.commits = {0: sos.CommitInfo(0, 0, "bla")}
        _.assertEqual(13, m.getRevisionByName("13"))
        _.assertEqual(0, m.getRevisionByName("bla"))
        _.assertEqual(-1, m.getRevisionByName(""))  # split from "/"

    def testTagging(_):
        m = sos.Metadata(os.getcwd())
        sos.offline()
        _.createFile(111)
        sos.commit("tag", ["--tag"])
        out = wrapChannels(lambda: sos.log()).replace("\r", "").split("\n")
        _.assertTrue(any(("|tag" in line and line.endswith("|TAG") for line in out)))
        _.createFile(2)
        try:
            sos.commit("tag")
            _.fail()
        except:
            pass
        sos.commit("tag-2", ["--tag"])
        out = wrapChannels(lambda: sos.ls(options=["--tags"])).replace("\r", "")
        _.assertIn("TAG tag", out)

    def testSwitch(_):
        _.createFile(1, "x" * 100)
        _.createFile(2, "y")
        sos.offline("test")  # file1-2  in initial branch commit
        sos.branch("second")  # file1-2  switch, having same files
        sos.switch("0")  # no change  switch back, no problem
        sos.switch("second")  # no change  # switch back, no problem
        _.createFile(3, "y")  # generate a file
        try:  # uncommited changes detected
            sos.switch("test")  # uncommited changes detected
            _.fail()  # uncommited changes detected
        except SystemExit as E:
            _.assertEqual(1, E.code)
        sos.commit("Finish")  # file1-3  commit third file into branch second
        sos.changes()
        sos.switch("test")  # file1-2, remove file3 from file tree
        _.assertFalse(_.existsFile(3))  # removed when switching back to test
        _.createFile("XXX")
        out = wrapChannels(lambda: sos.status()).replace("\r", "")
        _.assertIn("File tree has changes", out)
        _.assertNotIn("File tree is unchanged", out)
        _.assertIn("  * b00   'test'", out)
        _.assertIn("    b01 'second'", out)
        _.assertIn("(dirty)", out)  # one branch has commits
        _.assertIn("(in sync)", out)  # the other doesn't
        sos.defaults["useChangesCommand"] = False  # because sos.main() is never called
        out = wrapChannels(lambda: sos.status()).replace("\r", "")  # trigger repo info
        _.assertAllIn(["Metadata format", "Content checking:    deactivated", "Data compression:    deactivated", "Repository mode:     simple", "Number of branches:  2"], out)
        sos.defaults["useChangesCommand"] = True  # because sos.main() is never called
        _.createFile(4, "xy")  # generate a file
        sos.switch("second", ["--force"])  # avoids warning on uncommited changes, but keeps file4
        _.assertFalse(_.existsFile(4))  # removed when forcedly switching back to test
        _.assertTrue(_.existsFile(3))  # was restored from branch's revision r1
        os.unlink("." + os.sep + "file1")  # remove old file1
        sos.switch("test", ["--force"])  # should restore file1 and remove file3
        _.assertTrue(_.existsFile(1))  # was restored from branch's revision r1
        _.assertFalse(_.existsFile(3))  # was restored from branch's revision r1
        out = wrapChannels(lambda: sos.dump("dumped.sos.zip", options=["--skip-backup", "--full"])).replace("\r", "")
        _.assertAllIn(["Dumping revisions"], out)
        _.assertNotIn("Creating backup", out)
        out = wrapChannels(lambda: sos.dump("dumped.sos.zip", options=["--skip-backup"])).replace("\r", "")
        _.assertIn("Dumping revisions", out)
        _.assertNotIn("Creating backup", out)
        out = wrapChannels(lambda: sos.dump("dumped.sos.zip", options=["--full"])).replace("\r", "")
        _.assertAllIn(["Creating backup"], out)
        _.assertIn("Dumping revisions", out)

    def testAutoDetectVCS(_):
        os.mkdir(".git")
        sos.offline(sos.vcsBranches[sos.findSosVcsBase()[2]])  # create initial branch
        with open(sos.metaFolder + os.sep + sos.metaFile, "r") as fd:
            meta = fd.read()
        _.assertTrue("\"master\"" in meta)
        os.rmdir(".git")

    def testUpdate(_):
        sos.offline("trunk")  # create initial branch b0/r0
        _.createFile(1, "x" * 100)
        sos.commit("second")  # create b0/r1

        sos.switch("/0")  # go back to b0/r0 - deletes file1
        _.assertFalse(_.existsFile(1))

        sos.update("/1")  # recreate file1
        _.assertTrue(_.existsFile(1))

        sos.commit("third", ["--force"])  # force because nothing to commit. should create r2 with same contents as r1, but as differential from r1, not from r0 (= no changes in meta folder)
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 2)))
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 2, file=sos.metaFile)))
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 2))))  # only meta data file, no differential files

        sos.update("/1")  # do nothing, as nothing has changed
        _.assertTrue(_.existsFile(1))

        _.createFile(2, "y" * 100)
#    out = wrapChannels(() -> sos.branch("other"))  # won't comply as there are changes
#    _.assertIn("--force", out)
        sos.branch("other", options=["--force"])  # automatically including file 2 (as we are in simple mode)
        _.assertTrue(_.existsFile(2))
        sos.update("trunk", ["--add"])  # only add stuff
        _.assertTrue(_.existsFile(2))
        sos.update("trunk")  # nothing to do
        _.assertFalse(_.existsFile(2))  # removes file not present in original branch

        theirs = b"a\nb\nc\nd\ne\nf\ng\nh\nx\nx\nj\nk"
        _.createFile(10, theirs)
        mine = b"a\nc\nd\ne\ng\nf\nx\nh\ny\ny\nj"  # missing "b", inserted g, modified g->x, replace x/x -> y/y, removed k
        _.createFile(11, mine)
        _.assertEqual((b"a\nb\nc\nd\ne\nf\ng\nh\nx\nx\nj\nk", b"\n"), sos.merge(filename="." + os.sep + "file10", intoname="." + os.sep + "file11", mergeOperation=sos.MergeOperation.BOTH))  # completely recreated other file
        _.assertEqual((b'a\nb\nc\nd\ne\ng\nf\ng\nh\ny\ny\nx\nx\nj\nk', b"\n"), sos.merge(filename="." + os.sep + "file10", intoname="." + os.sep + "file11", mergeOperation=sos.MergeOperation.INSERT))

    def testUpdate2(_):
        _.createFile("test.txt", "x" * 10)
        sos.offline("trunk", ["--strict"])  # use strict mode, as timestamp differences are too small for testing
        sync()
        sos.branch("mod")
        _.createFile("test.txt", "x" * 5 + "y" * 5)
        sos.commit("mod")  # create b0/r1
        sos.switch("trunk", ["--force"])  # should replace contents, force in case some other files were modified (e.g. during working on the code) TODO investigate more
        _.assertTrue(_.existsFile("test.txt", b"x" * 10))
        sos.update("mod")  # integrate changes TODO same with ask -> theirs
        _.existsFile("test.txt", b"x" * 5 + b"y" * 5)
        _.createFile("test.txt", "x" * 10)
        mockInput(["t"], lambda: sos.update("mod", ["--ask-lines"]))
        sync()
        _.assertTrue(_.existsFile("test.txt", b"x" * 5 + b"y" * 5))
        _.createFile("test.txt", "x" * 5 + "z" + "y" * 4)
        sos.update("mod")  # auto-insert/removes (no intra-line conflict)
        _.createFile("test.txt", "x" * 5 + "z" + "y" * 4)
        sync()
        mockInput(["t"], lambda: sos.update("mod", ["--ask"]))  # same as above with interaction -> use theirs (overwrite current file state)
        _.assertTrue(_.existsFile("test.txt", b"x" * 5 + b"y" * 5))

    def testIsTextType(_):
        m = sos.Metadata(".")
        m.c.texttype = ["*.x", "*.md", "*.md.*"]
        m.c.bintype = ["*.md.confluence"]
        _.assertTrue(m.isTextType("ab.txt"))
        _.assertTrue(m.isTextType("./ab.txt"))
        _.assertTrue(m.isTextType("bc/ab.txt"))
        _.assertFalse(m.isTextType("bc/ab."))
        _.assertTrue(m.isTextType("23_3.x.x"))
        _.assertTrue(m.isTextType("dfg/dfglkjdf7/test.md"))
        _.assertTrue(m.isTextType("./test.md.pdf"))
        _.assertFalse(m.isTextType("./test_a.md.confluence"))

    def testEolDet(_):
        ''' Check correct end-of-line detection. '''
        _.assertEqual(b"\n", sos.eoldet(b"a\nb"))
        _.assertEqual(b"\r\n", sos.eoldet(b"a\r\nb\r\n"))
        _.assertEqual(b"\r", sos.eoldet(b"\ra\rb"))
        _.assertAllIn(["Inconsistent", "with "], wrapChannels(lambda: _.assertEqual(b"\n", sos.eoldet(b"\r\na\r\nb\n"))))
        _.assertAllIn(["Inconsistent", "without"], wrapChannels(lambda: _.assertEqual(b"\n", sos.eoldet(b"\ra\nnb\n"))))
        _.assertIsNone(sos.eoldet(b""))
        _.assertIsNone(sos.eoldet(b"sdf"))

    def testMerge(_):
        ''' Check merge results depending on user options. '''
        a = b"a\nb\ncc\nd"  # type: bytes
        b = b"a\nb\nee\nd"  # type: bytes  # replaces cc by ee
        _.assertEqual(b"a\nb\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT)[0])  # one-line block replacement using lineMerge
        _.assertEqual(b"a\nb\neecc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT, charMergeOperation=sos.MergeOperation.INSERT)[0])  # means insert changes from a into b, but don't replace
        _.assertEqual(b"a\nb\n\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT, charMergeOperation=sos.MergeOperation.REMOVE)[0])  # means insert changes from a into b, but don't replace
        _.assertEqual(b"a\nb\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE)[0])  # one-line block replacement using lineMerge
        _.assertEqual(b"a\nb\n\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE, charMergeOperation=sos.MergeOperation.REMOVE)[0])
        _.assertEqual(a, sos.merge(a, b, mergeOperation=sos.MergeOperation.BOTH)[0])  # keeps any changes in b
        a = b"a\nb\ncc\nd"
        b = b"a\nb\nee\nf\nd"  # replaces cc by block of two lines ee, f
        _.assertEqual(b"a\nb\nee\nf\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT)[0])  # multi-line block replacement
        _.assertEqual(b"a\nb\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE)[0])
        _.assertEqual(a, sos.merge(a, b, mergeOperation=sos.MergeOperation.BOTH)[0])  # keeps any changes in b
# Test with change + insert
        _.assertEqual(b"a\nb fdcd d\ne", sos.merge(b"a\nb cd d\ne", b"a\nb fdd d\ne", charMergeOperation=sos.MergeOperation.INSERT)[0])
        _.assertEqual(b"a\nb d d\ne", sos.merge(b"a\nb cd d\ne", b"a\nb fdd d\ne", charMergeOperation=sos.MergeOperation.REMOVE)[0])
# Test interactive merge
        a = b"a\nb\nb\ne"  # block-wise replacement
        b = b"a\nc\ne"
        _.assertEqual(b, mockInput(["i"], lambda: sos.merge(a, b, mergeOperation=sos.MergeOperation.ASK)[0]))
        _.assertEqual(a, mockInput(["t"], lambda: sos.merge(a, b, mergeOperation=sos.MergeOperation.ASK)[0]))
        a = b"a\nb\ne"  # intra-line merge
        _.assertEqual(b, mockInput(["i"], lambda: sos.merge(a, b, charMergeOperation=sos.MergeOperation.ASK)[0]))
        _.assertEqual(a, mockInput(["t"], lambda: sos.merge(a, b, charMergeOperation=sos.MergeOperation.ASK)[0]))

    def testMergeEol(_):
        _.assertEqual(b"\r\n", sos.merge(b"a\nb", b"a\r\nb")[1])
        _.assertIn("Differing EOL-styles", wrapChannels(lambda: sos.merge(b"a\nb", b"a\r\nb")))  # expects a warning
        _.assertIn(b"a\r\nb", sos.merge(b"a\nb", b"a\r\nb")[0])  # when in doubt, use "mine" CR-LF
        _.assertIn(b"a\nb", sos.merge(b"a\nb", b"a\r\nb", eol=True)[0])
        _.assertEqual(b"\n", sos.merge(b"a\nb", b"a\r\nb", eol=True)[1])

    def testPickyMode(_):
        ''' Confirm that picky mode reset tracked patterns after commits. '''
        sos.offline("trunk", None, ["--picky"])
        changes = sos.changes()
        _.assertEqual(0, len(changes.additions))  # do not list any existing file as an addition
        sos.add(".", "./file?", ["--force"])
        _.createFile(1, "aa")
        sos.commit("First")  # add one file
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))
        _.createFile(2, "b")
        try:  # add nothing, because picky
            sos.commit("Second")  # add nothing, because picky
        except:
            pass
        sos.add(".", "./file?")
        sos.commit("Third")
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 2))))
        out = wrapChannels(lambda: sos.log([])).replace("\r", "")
        _.assertIn("  * r2", out)
        _.createFile(3, prefix="sub")
        sos.add("sub", "sub/file?")
        changes = sos.changes()
        _.assertEqual(1, len(changes.additions))
        _.assertTrue("sub/file3" in changes.additions)

    def testTrackedSubfolder(_):
        ''' See if patterns for files in sub folders are picked up correctly. '''
        os.mkdir("." + os.sep + "sub")
        sos.offline("trunk", None, ["--track"])
        _.createFile(1, "x")
        _.createFile(1, "x", prefix="sub")
        sos.add(".", "./file?")  # add glob pattern to track
        sos.commit("First")
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # one new file + meta file
        sos.add(".", "sub/file?")  # add glob pattern to track
        sos.commit("Second")  # one new file + meta
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # one new file + meta file
        os.unlink("file1")  # remove from basefolder
        _.createFile(2, "y")
        sos.remove(".", "sub/file?")
        try:  # raises Exit. TODO test the "suggest a pattern" case
            sos.remove(".", "sub/bla")  # raises Exit. TODO test the "suggest a pattern" case
            _.fail()  # raises Exit. TODO test the "suggest a pattern" case
        except:
            pass
        sos.commit("Third")
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 2))))  # one new file + meta
# TODO also check if /file1 and sub/file1 were removed from index

    def testTrackedMode(_):
        ''' Difference in semantics vs simple mode:
          - For remote/other branch we can only know and consider tracked files, thus ignoring all complexity stemming from handling addition of untracked files.
          - For current branch, we can take into account tracked and untracked ones, in theory, but it doesn't make sense.
        In conclusion, using the union of tracking patterns from both sides to find affected files makes sense, but disallow deleting files not present in remote branch.
    '''
        sos.offline("test", options=["--track"])  # set up repo in tracking mode (SVN- or gitless-style)
        _.createFile(1)
        _.createFile("a123a")  # untracked file "a123a"
        sos.add(".", "./file?")  # add glob tracking pattern
        sos.commit("second")  # versions "file1"
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # one new file + meta file
        out = wrapChannels(lambda: sos.status()).replace("\r", "")
        _.assertIn("  | ./file?", out)

        _.createFile(2)  # untracked file "file2"
        sos.commit("third")  # versions "file2"
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 2))))  # one new file + meta file

        os.mkdir("." + os.sep + "sub")
        _.createFile(3, prefix="sub")  # untracked file "sub/file3"
        sos.commit("fourth", ["--force"])  # no tracking pattern matches the subfolder
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 3))))  # meta file only, no other tracked path/file

        sos.branch("Other")  # second branch containing file1 and file2 tracked by "./file?"
        sos.remove(".", "./file?")  # remove tracking pattern, but don't touch previously created and versioned files
        sos.add(".", "./a*a")  # add tracking pattern
        changes = sos.changes()  # should pick up addition only, because tracked, but not the deletion, as not tracked anymore
        _.assertEqual(0, len(changes.modifications))
        _.assertEqual(0, len(changes.deletions))  # not tracked anymore, but contained in version history and not removed
        _.assertEqual(1, len(changes.additions))  # detected one addition "a123a", but won't recognize untracking files as deletion

        sos.commit("Second_2")
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(1, 1))))  # "a123a" + meta file
        _.existsFile(1, b"x" * 10)
        _.existsFile(2, b"x" * 10)

        sos.switch("test")  # go back to first branch - tracks only "file?", but not "a*a"
        _.existsFile(1, b"x" * 10)
        _.existsFile("a123a", b"x" * 10)

        sos.update("Other")  # integrate tracked files and tracking pattern from second branch into working state of master branch
        _.assertTrue(os.path.exists("." + os.sep + "file1"))
        _.assertTrue(os.path.exists("." + os.sep + "a123a"))

        _.createFile("axxxa")  # new file that should be tracked on "test" now that we integrated "Other"
        sos.commit("fifth")  # create new revision after integrating updates from second branch
        _.assertEqual(3, len(os.listdir(sos.revisionFolder(0, 4))))  # one new file from other branch + one new in current folder + meta file
        sos.switch("Other")  # switch back to just integrated branch that tracks only "a*a" - shouldn't do anything
        _.assertTrue(os.path.exists("." + os.sep + "file1"))
        _.assertTrue(os.path.exists("." + os.sep + "a123a"))
        _.assertFalse(os.path.exists("." + os.sep + "axxxa"))  # because tracked in both branches, but not present in other -> delete in file tree
# TODO test switch --meta

    def testLsTracked(_):
        sos.offline("test", options=["--track"])  # set up repo in tracking mode (SVN- or gitless-style)
        _.createFile(1)
        _.createFile("foo")
        sos.add(".", "./file*")  # capture one file
        sos.ls()
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")
        _.assertInAny("TRK file1  (file*)", out)
        _.assertNotInAny("... file1  (file*)", out)
        _.assertInAny("    foo", out)
        out = sos.safeSplit(wrapChannels(lambda: sos.ls(options=["--patterns"])).replace("\r", ""), "\n")
        _.assertInAny("TRK file*", out)
        _.createFile("a", prefix="sub")
        sos.add("sub", "sub/a")
        sos.ls("sub")
        _.assertIn("TRK a  (a)", sos.safeSplit(wrapChannels(lambda: sos.ls("sub")).replace("\r", ""), "\n"))

    def testLineMerge(_):
        _.assertEqual("xabc", sos.lineMerge("xabc", "a bd"))
        _.assertEqual("xabxxc", sos.lineMerge("xabxxc", "a bd"))
        _.assertEqual("xa bdc", sos.lineMerge("xabc", "a bd", mergeOperation=sos.MergeOperation.INSERT))
        _.assertEqual("ab", sos.lineMerge("xabc", "a bd", mergeOperation=sos.MergeOperation.REMOVE))

    def testCompression(_):  # TODO test output ratio/advantage, also depending on compress flag set or not
        _.createFile(1)
        sos.offline("master", options=["--force"])
        out = wrapChannels(lambda: sos.changes(options=['--progress'])).replace("\r", "").split("\n")
        _.assertFalse(any(("Compression advantage" in line for line in out)))  # simple mode should always print this to stdout
        _.assertTrue(_.existsFile(sos.revisionFolder(0, 0, file="b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"), b"x" * 10))
        setRepoFlag("compress", True)  # was plain = uncompressed before
        _.createFile(2)
        out = wrapChannels(lambda: sos.commit("Added file2", options=['--progress'])).replace("\r", "").split("\n")
        _.assertTrue(any(("Compression advantage" in line for line in out)))
        _.assertTrue(_.existsFile(sos.revisionFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2")))  # exists
        _.assertFalse(_.existsFile(sos.revisionFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2"), b"x" * 10))  # but is compressed instead

    def testLocalConfig(_):
        sos.offline("bla", options=[])
        try:
            sos.config(["set", "ignores", "one;two"], options=["--local"])
        except SystemExit as E:
            _.assertEqual(0, E.code)
        _.assertTrue(checkRepoFlag("ignores", value=["one", "two"]))

    def testConfigVariations(_):
        def makeRepo():
            try:
                os.unlink("file1")
            except:
                pass
            sos.offline("master", options=["--force"])
            _.createFile(1)
            sos.commit("Added file1")
        try:
            sos.config(["set", "strict", "on"])
        except SystemExit as E:
            _.assertEqual(0, E.code)
        makeRepo()
        _.assertTrue(checkRepoFlag("strict", True))
        try:
            sos.config(["set", "strict", "off"])
        except SystemExit as E:
            _.assertEqual(0, E.code)
        makeRepo()
        _.assertTrue(checkRepoFlag("strict", False))
        try:
            sos.config(["set", "strict", "yes"])
        except SystemExit as E:
            _.assertEqual(0, E.code)
        makeRepo()
        _.assertTrue(checkRepoFlag("strict", True))
        try:
            sos.config(["set", "strict", "no"])
        except SystemExit as E:
            _.assertEqual(0, E.code)
        makeRepo()
        _.assertTrue(checkRepoFlag("strict", False))
        try:
            sos.config(["set", "strict", "1"])
        except SystemExit as E:
            _.assertEqual(0, E.code)
        makeRepo()
        _.assertTrue(checkRepoFlag("strict", True))
        try:
            sos.config(["set", "strict", "0"])
        except SystemExit as E:
            _.assertEqual(0, E.code)
        makeRepo()
        _.assertTrue(checkRepoFlag("strict", False))
        try:
            sos.config(["set", "strict", "true"])
        except SystemExit as E:
            _.assertEqual(0, E.code)
        makeRepo()
        _.assertTrue(checkRepoFlag("strict", True))
        try:
            sos.config(["set", "strict", "false"])
        except SystemExit as E:
            _.assertEqual(0, E.code)
        makeRepo()
        _.assertTrue(checkRepoFlag("strict", False))
        try:
            sos.config(["set", "strict", "enable"])
        except SystemExit as E:
            _.assertEqual(0, E.code)
        makeRepo()
        _.assertTrue(checkRepoFlag("strict", True))
        try:
            sos.config(["set", "strict", "disable"])
        except SystemExit as E:
            _.assertEqual(0, E.code)
        makeRepo()
        _.assertTrue(checkRepoFlag("strict", False))
        try:
            sos.config(["set", "strict", "enabled"])
        except SystemExit as E:
            _.assertEqual(0, E.code)
        makeRepo()
        _.assertTrue(checkRepoFlag("strict", True))
        try:
            sos.config(["set", "strict", "disabled"])
        except SystemExit as E:
            _.assertEqual(0, E.code)
        makeRepo()
        _.assertTrue(checkRepoFlag("strict", False))
        try:
            sos.config(["set", "strict", "nope"])
            _.fail()
        except SystemExit as E:
            _.assertEqual(1, E.code)

    def testLsSimple(_):
        _.createFile(1)
        _.createFile("foo")
        _.createFile("ign1")
        _.createFile("ign2")
        _.createFile("bar", prefix="sub")
        sos.offline("test")  # set up repo in tracking mode (SVN- or gitless-style)
        try:  # define an ignore pattern
            sos.config(["set", "ignores", "ign1"])  # define an ignore pattern
        except SystemExit as E:
            _.assertEqual(0, E.code)
        try:  # additional ignore pattern
            sos.config(["add", "ignores", "ign2"])  # additional ignore pattern
        except SystemExit as E:
            _.assertEqual(0, E.code)
        try:  # define a list of ignore patterns
            sos.config(["set", "ignoresWhitelist", "ign1;ign2"])  # define a list of ignore patterns
        except SystemExit as E:
            _.assertEqual(0, E.code)
        out = wrapChannels(lambda: sos.config(["show"])).replace("\r", "")
        _.assertIn("             ignores [global]  ['ign1', 'ign2']", out)
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")
        _.assertInAny('    file1', out)
        _.assertInAny('    ign1', out)
        _.assertInAny('    ign2', out)
        _.assertNotIn('DIR sub', out)
        _.assertNotIn('    bar', out)
        out = wrapChannels(lambda: sos.ls(options=["--recursive"])).replace("\r", "")
        _.assertIn('DIR sub', out)
        _.assertIn('    bar', out)
        try:
            sos.config(["rm", "foo", "bar"])
            _.fail()
        except SystemExit as E:
            _.assertEqual(1, E.code)
        try:
            sos.config(["rm", "ignores", "foo"])
            _.fail()
        except SystemExit as E:
            _.assertEqual(1, E.code)
        try:
            sos.config(["rm", "ignores", "ign1"])
        except SystemExit as E:
            _.assertEqual(0, E.code)
        try:  # remove ignore pattern
            sos.config(["unset", "ignoresWhitelist"])  # remove ignore pattern
        except SystemExit as E:
            _.assertEqual(0, E.code)
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")
        _.assertInAny('    ign1', out)
        _.assertInAny('IGN ign2', out)
        _.assertNotInAny('    ign2', out)

    def testWhitelist(_):
# TODO test same for simple mode
        _.createFile(1)
        sos.defaults.ignores[:] = ["file*"]  # replace in-place
        sos.offline("xx", options=["--track", "--strict"])  # because nothing to commit due to ignore pattern
        sos.add(".", "./file*")  # add tracking pattern for "file1"
        sos.commit(options=["--force"])  # attempt to commit the file
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 1))))  # only meta data, file1 was ignored
        try:  # Exit because dirty
            sos.online()  # Exit because dirty
            _.fail()  # Exit because dirty
        except:  # exception expected
            pass  # exception expected
        _.createFile("x2")  # add another change
        sos.add(".", "./x?")  # add tracking pattern for "file1"
        try:  # force beyond dirty flag check
            sos.online(["--force"])  # force beyond dirty flag check
            _.fail()  # force beyond dirty flag check
        except:
            pass
        sos.online(["--force", "--force"])  # force beyond file tree modifications check
        _.assertFalse(os.path.exists(sos.metaFolder))

        _.createFile(1)
        sos.defaults.ignoresWhitelist[:] = ["file*"]
        sos.offline("xx", None, ["--track"])
        sos.add(".", "./file*")
        sos.commit()  # should NOT ask for force here
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # meta data and "file1", file1 was whitelisted

    def testRemove(_):
        _.createFile(1, "x" * 100)
        sos.offline("trunk")
        try:
            sos.destroy("trunk")
            _fail()
        except:
            pass
        _.createFile(2, "y" * 10)
        sos.branch("added")  # creates new branch, writes repo metadata, and therefore creates backup copy
        sos.destroy("trunk")
        _.assertAllIn([sos.metaFile, sos.metaBack, "b0_last", "b1"], os.listdir("." + os.sep + sos.metaFolder))
        _.assertTrue(os.path.exists("." + os.sep + sos.metaFolder + os.sep + "b1"))
        _.assertFalse(os.path.exists("." + os.sep + sos.metaFolder + os.sep + "b0"))
        sos.branch("next")
        _.createFile(3, "y" * 10)  # make a change
        sos.destroy("added", "--force")  # should succeed

    def testUsage(_):
        try:  # TODO expect sys.exit(0)
            sos.usage()  # TODO expect sys.exit(0)
            _.fail()  # TODO expect sys.exit(0)
        except:
            pass
        try:
            sos.usage(short=True)
            _.fail()
        except:
            pass

    def testOnlyExcept(_):
        ''' Test blacklist glob rules. '''
        sos.offline(options=["--track"])
        _.createFile("a.1")
        _.createFile("a.2")
        _.createFile("b.1")
        _.createFile("b.2")
        sos.add(".", "./a.?")
        sos.add(".", "./?.1", negative=True)
        out = wrapChannels(lambda: sos.commit())
        _.assertIn("ADD ./a.2", out)
        _.assertNotIn("ADD ./a.1", out)
        _.assertNotIn("ADD ./b.1", out)
        _.assertNotIn("ADD ./b.2", out)

    def testOnly(_):
        _.assertEqual((_coconut.frozenset(("./A", "x/B")), _coconut.frozenset(("./C",))), sos.parseOnlyOptions(".", ["abc", "def", "--only", "A", "--x", "--only", "x/B", "--except", "C", "--only"]))
        _.assertEqual(_coconut.frozenset(("B",)), sos.conditionalIntersection(_coconut.frozenset(("A", "B", "C")), _coconut.frozenset(("B", "D"))))
        _.assertEqual(_coconut.frozenset(("B", "D")), sos.conditionalIntersection(_coconut.frozenset(), _coconut.frozenset(("B", "D"))))
        _.assertEqual(_coconut.frozenset(("B", "D")), sos.conditionalIntersection(None, _coconut.frozenset(("B", "D"))))
        sos.offline(options=["--track", "--strict"])
        _.createFile(1)
        _.createFile(2)
        sos.add(".", "./file1")
        sos.add(".", "./file2")
        sos.commit(onlys=_coconut.frozenset(("./file1",)))
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # only meta and file1
        sos.commit()  # adds also file2
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 2))))  # only meta and file1
        _.createFile(1, "cc")  # modify both files
        _.createFile(2, "dd")
        try:
            sos.config(["set", "texttype", "file2"])
        except SystemExit as E:
            _.assertEqual(0, E.code)
        changes = sos.changes(excps=_coconut.frozenset(("./file1",)))
        _.assertEqual(1, len(changes.modifications))  # only file2
        _.assertTrue("./file2" in changes.modifications)
        _.assertAllIn(["DIF ./file2", "<No newline>"], wrapChannels(lambda: sos.diff(onlys=_coconut.frozenset(("./file2",)))))
        _.assertAllNotIn(["MOD ./file1", "DIF ./file1", "MOD ./file2"], wrapChannels(lambda: sos.diff(onlys=_coconut.frozenset(("./file2",)))))

    def testDiff(_):
        try:  # manually mark this file as "textual"
            sos.config(["set", "texttype", "file1"])  # manually mark this file as "textual"
        except SystemExit as E:
            _.assertEqual(0, E.code)
        sos.offline(options=["--strict"])
        _.createFile(1)
        _.createFile(2)
        sos.commit()
        _.createFile(1, "sdfsdgfsdf")
        _.createFile(2, "12343")
        sos.commit()
        _.createFile(1, "foobar")
        _.createFile(3)
        out = wrapChannels(lambda: sos.diff("/-2"))  # compare with r1 (second counting from last which is r2)
        _.assertIn("ADD ./file3", out)
        _.assertAllIn(["MOD ./file2", "DIF ./file1  <No newline>", "- | 0 |xxxxxxxxxx|", "+ | 0 |foobar|"], out)
        _.assertAllNotIn(["MOD ./file1", "DIF ./file1"], wrapChannels(lambda: sos.diff("/-2", onlys=_coconut.frozenset(("./file2",)))))

    def testReorderRenameActions(_):
        result = sos.reorderRenameActions([("123", "312"), ("312", "132"), ("321", "123")], exitOnConflict=False)  # type: Tuple[str, str]
        _.assertEqual([("312", "132"), ("123", "312"), ("321", "123")], result)
        try:
            sos.reorderRenameActions([("123", "312"), ("312", "123")], exitOnConflict=True)
            _.fail()
        except:
            pass

    def testMove(_):
        sos.offline(options=["--strict", "--track"])
        _.createFile(1)
        sos.add(".", "./file?")
# test source folder missing
        try:
            sos.move("sub", "sub/file?", ".", "?file")
            _.fail()
        except:
            pass
# test target folder missing: create it
        sos.move(".", "./file?", "sub", "sub/file?")
        _.assertTrue(os.path.exists("sub"))
        _.assertTrue(os.path.exists("sub/file1"))
        _.assertFalse(os.path.exists("file1"))
# test move
        sos.move("sub", "sub/file?", ".", "./?file")
        _.assertTrue(os.path.exists("1file"))
        _.assertFalse(os.path.exists("sub/file1"))
# test nothing matches source pattern
        try:
            sos.move(".", "a*", ".", "b*")
            _.fail()
        except:
            pass
        sos.add(".", "*")  # anything pattern
        try:  # TODO check that alternative pattern "*" was suggested (1 hit)
            sos.move(".", "a*", ".", "b*")  # TODO check that alternative pattern "*" was suggested (1 hit)
            _.fail()  # TODO check that alternative pattern "*" was suggested (1 hit)
        except:
            pass
# test rename no conflict
        _.createFile(1)
        _.createFile(2)
        _.createFile(3)
        sos.add(".", "./file*")
        try:  # define an ignore pattern
            sos.config(["set", "ignores", "file3;file4"])  # define an ignore pattern
        except SystemExit as E:
            _.assertEqual(0, E.code)
        try:
            sos.config(["set", "ignoresWhitelist", "file3"])
        except SystemExit as E:
            _.assertEqual(0, E.code)
        sos.move(".", "./file*", ".", "fi*le")
        _.assertTrue(all((os.path.exists("fi%dle" % i) for i in range(1, 4))))
        _.assertFalse(os.path.exists("fi4le"))
# test rename solvable conflicts
        [_.createFile("%s-%s-%s" % tuple((c for c in n))) for n in ["312", "321", "123", "231"]]
#    sos.move("?-?-?")
# test rename unsolvable conflicts
# test --soft option
        sos.remove(".", "./?file")  # was renamed before
        sos.add(".", "./?a?b", ["--force"])
        sos.move(".", "./?a?b", ".", "./a?b?", ["--force", "--soft"])
        _.createFile("1a2b")  # should not be tracked
        _.createFile("a1b2")  # should be tracked
        sos.commit()
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 1, file="93b38f90892eb5c57779ca9c0b6fbdf6774daeee3342f56f3e78eb2fe5336c50")))  # a1b2
        _.createFile("1a1b1")
        _.createFile("1a1b2")
        sos.add(".", "?a?b*")
        _.assertIn("not unique", wrapChannels(lambda: sos.move(".", "?a?b*", ".", "z?z?")))  # should raise error due to same target name
# TODO only rename if actually any files are versioned? or simply what is alife?
# TODO add test if two single question marks will be moved into adjacent characters

    def testHashCollision(_):
        sos.offline()
        _.createFile(1)
        os.mkdir(sos.revisionFolder(0, 1))
        _.createFile("b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa", prefix=sos.revisionFolder(0, 1))
        _.createFile(1)
        try:  # should exit with error due to collision detection
            sos.commit()  # should exit with error due to collision detection
            _.fail()  # should exit with error due to collision detection
        except SystemExit as E:  # TODO will capture exit(0) which is wrong, change to check code in all places
            _.assertEqual(1, E.code)  # TODO will capture exit(0) which is wrong, change to check code in all places

    def testFindBase(_):
        old = os.getcwd()
        try:
            os.mkdir("." + os.sep + ".git")
            os.makedirs("." + os.sep + "a" + os.sep + sos.metaFolder)
            os.makedirs("." + os.sep + "a" + os.sep + "b")
            os.chdir("a" + os.sep + "b")
            s, vcs, cmd = sos.findSosVcsBase()
            _.assertIsNotNone(s)
            _.assertIsNotNone(vcs)
            _.assertEqual("git", cmd)
        finally:
            os.chdir(old)

# TODO test command line operation --sos vs. --vcs
# check exact output instead of only expected exception/fail

# TODO test +++ --- in diff
# TODO test +01/-02/*..
# TODO tests for loadcommit redirection
# TODO test wrong branch/revision after fast branching, would raise exception for -1 otherwise

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, stream=sys.stderr, format="%(asctime)-23s %(levelname)-8s %(name)s:%(lineno)d | %(message)s" if '--log' in sys.argv else "%(message)s")
    c = configr.Configr("sos")
    c.loadSettings()
    if len(c.keys()) > 0:
        sos.Exit("Cannot run test suite with existing local SOS user configuration (would affect results)")
    unittest.main(testRunner=debugTestRunner() if '-v' in sys.argv and not os.getenv("CI", "false").lower() == "true" else None)  # warnings = "ignore")
