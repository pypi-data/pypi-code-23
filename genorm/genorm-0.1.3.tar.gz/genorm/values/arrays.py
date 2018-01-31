import os
import os.path
import math
import json
from pc23 import xrange
from .base import AttributeValueVirtual, ValueArrayAbstract, AttributeValueNull
from ..exceptions import OrmValueError, OrmUnacceptableOperation, OrmNotDefinedYet, OrmParameterError
from ..manage import manager


class ValueList(ValueArrayAbstract, list):
    def __init__(self):
        super(ValueList, self).__init__()
        self._objects = list()
        self._original_values = list()
        self._values = list()

    def __repr__(self):
        return "List(%r)" % self._values

    def _update_objects_pos(self):
        sz = len(self._objects)
        if sz > 0:
            for n in xrange(sz):
                self._objects[n].pos = n

    def reset(self):
        self._objects = list()
        self._to_delete = list()
        self._loaded = False
        self._values = list()

    def write(self):
        self._update_objects_pos()
        super(ValueList, self).write()

    def load(self):
        from ..funcs import where_
        c = self._get_c()
        if c is None or self.instance is None:
            return
        self._loaded = True
        model = self.instance.__class__
        session = manager.get_session(instance=self.instance)
        pk = model.__meta__.primary_key
        w = list()
        for k in pk:
            w.append(getattr(c.array_model, 'parent_%s' % k) == getattr(self.instance, k))
        objects = session.select(c.array_model).where(where_(*w)).order_by(getattr(c.array_model, 'pos')).go()
        self._values = list()
        for o in objects:
            value = getattr(o, 'value')
            self._values.append(value)
            self._objects.append(o)
        self._update_objects_pos()
        self._original_values = list(self._values)

    def __contains__(self, x):
        self.ensure()
        return x in self._values

    def __delitem__(self, i):
        self.delete(i)

    def __delslice__(self, i, j):
        # TODO !
        pass

    def __getitem__(self, i):
        return self.get(i)

    def __getslice__(self, i, j):
        # TODO !
        pass

    def __iter__(self):
        self.ensure()
        for x in self._values:
            yield x

    def __len__(self):
        self.ensure()
        return 0 if self._values is None else len(self._values)

    def __reversed__(self):
        return self._values.__reversed__()

    def __setitem__(self, i, x):
        self.set(i, x)

    def append(self, x):
        self.ensure()
        c = self._get_c()
        if c is None:
            raise OrmNotDefinedYet("cannot access values of List until model been defined!")
        if c.unique and x in self._values:
            return
        obj = self.c.array_model()
        self._assign_with_instance(obj)
        obj.value = x
        self._objects.append(obj)
        self._values.append(x)
        self._update_objects_pos()
        self._verify_changes()

    def delete(self, i):
        self.ensure()
        if i >= len(self._values):
            raise IndexError(i)
        obj = self._objects[i]
        self._to_delete.append(obj)
        del (self._values[i])
        del (self._objects[i])
        self._update_objects_pos()
        self._verify_changes()

    def remove(self, x):
        self.ensure()
        if x not in self._values:
            raise KeyError(x)
        self.delete(self._values.index(x))

    def set(self, i, x):
        self.ensure()
        if i >= len(self._values):
            raise IndexError(i)
        i_ = self._values.index(x)
        if i_ and i_ != i:
            raise OrmValueError("value is already exists in the unique List: '%r'!" % x)
        self._values[i] = x
        self._objects[i].value = x
        self._verify_changes()

    def get(self, i):
        self.ensure()
        if i >= len(self._values):
            raise IndexError(i)
        return self._values[i]

    def count(self, x):
        self.ensure()
        return self._values.count(x)

    def extend(self, iterable):
        for x in iterable:
            self.append(x)

    def index(self, x, start=None, stop=None):
        return self._values.index(x, start, stop)

    def insert(self, i, x):
        self.ensure()
        c = self._get_c()
        if c is None:
            raise OrmNotDefinedYet("cannot access values of List until model been defined!")
        if c.unique and x in self._values:
            return
        obj = self.c.array_model()
        self._assign_with_instance(obj)
        obj.value = x
        self._objects.insert(i, obj)
        self._values.insert(i, x)
        self._update_objects_pos()
        self._verify_changes()

    def pop(self, i: int = -1):
        raise OrmUnacceptableOperation("cannot 'pop()' from the List!")

    def reverse(self):
        self.ensure()
        self._values.reverse()
        self._objects.reverse()
        self._update_objects_pos()
        self._verify_changes()

    def sort(self, cmp=None, key=None, reverse=False):
        raise OrmUnacceptableOperation("cannot 'sort()' List attribute!")


class ValueDict(ValueArrayAbstract, dict):
    def __init__(self):
        super(ValueDict, self).__init__()
        self._objects = dict()
        self._original_values = dict()
        self._values = dict()

    def __repr__(self):
        return "Dict(%r)" % self._values

    def load(self):
        from ..funcs import where_
        c = self._get_c()
        if c is None or self.instance is None:
            return
        self._loaded = True
        model = self.instance.__class__
        session = manager.get_session(instance=self.instance)
        pk = model.__meta__.primary_key
        w = list()
        for k in pk:
            w.append(getattr(c.array_model, 'parent_%s' % k) == getattr(self.instance, k))
        objects = session.select(c.array_model).where(where_(*w)).go()
        self._values = dict()
        for o in objects:
            key = getattr(o, '_k_')
            value = getattr(o, '_v_')
            self._values[key] = value
            self._objects[key] = o
        self._original_values = self._values.copy()

    def reset(self):
        self._objects = dict()
        self._to_delete = list()
        self._values = dict()
        self._loaded = False

    def get(self, key, default=None):
        self.ensure()
        return default if key not in self._values else self._values[key]

    def set(self, key, value):
        self.ensure()
        if key in self._values:
            obj = self._objects[key]
            setattr(obj, key, value)
        else:
            c = self._get_c()
            if c is None:
                raise OrmNotDefinedYet("cannot access values of Dict until model been defined!")
            obj = self.c.array_model()
            self._assign_with_instance(obj)
            obj._k_ = key
            obj._v_ = value
            self._objects[key] = obj
        self._values[key] = value
        self._verify_changes()

    def has(self, key):
        self.ensure()
        return key in self._values

    def delete(self, key):
        self.ensure()
        if key not in self._values:
            raise KeyError(key)
        obj = self._objects[key]
        self._to_delete.append(obj)
        del (self._objects[key])
        del (self._values[key])
        self._verify_changes()

    def __contains__(self, key):
        return self.has(key)

    def __delitem__(self, key):
        self.delete(key)

    def __getitem__(self, key):
        return self.get(key)

    def __iter__(self):
        self.ensure()
        for k in self._values:
            yield k

    def __len__(self):
        self.ensure()
        return 0 if self._values is None else len(self._values)

    def __setitem__(self, key, value):
        self.set(key, value)

    def clear(self):
        self.ensure()
        keys = self._values.keys()
        for k in keys:
            self.delete(k)

    def copy(self):
        self.ensure()
        return self._values.copy()

    def has_key(self, key):
        self.ensure()
        return self.has(key)

    def items(self):
        self.ensure()
        return self._values.items()

    def keys(self):
        self.ensure()
        return self._values.keys()

    def pop(self, key, default=None):
        raise OrmUnacceptableOperation("cannot 'pop()' from the Dict() attribute type!")

    def popitem(self):
        raise OrmUnacceptableOperation("cannot 'popitem()' from the Dict() attribute type!")

    def setdefault(self, key, default=None):
        self.ensure()
        if not self.has(key):
            self.set(key, default)
        return self.get(key)

    def update(self, **kwargs):
        self.ensure()
        for k in kwargs:
            v = kwargs[k]
            self.set(k, v)

    def values(self):
        self.ensure()
        return self._values.values()


class ValueMatrixRow(dict):
    """ The class representing a single row of values of the Matrix attribute. While it is basing on the
    dict, the difference is that this row disallows deletion or adding of keys (the set of keys is basing
    on the defined attribute's columns) and all changes in the row automatically are reflected in the
    corresponding real database object. """

    def __init__(self):
        super(ValueMatrixRow, self).__init__()
        self.instance = None
        self.model_k = None
        self.c = None
        self.obj = None

    def __setitem__(self, key, value):
        if key not in self.c.columns:
            raise KeyError(key)
        super(ValueMatrixRow, self).__setitem__(key, value)
        setattr(self.obj, key, value)

    def __contains__(self, key):
        return key in self.c.columns

    def __delitem__(self, key):
        raise OrmUnacceptableOperation("cannot delete key the of matrix row!")

    def clear(self):
        raise OrmUnacceptableOperation("cannot 'clear()' the of matrix row!")

    def has_key(self, key):
        return key in self.c.columns

    def pop(self, key, default=None):
        raise OrmUnacceptableOperation("cannot 'pop()' from the Dict() attribute type!")

    def popitem(self):
        raise OrmUnacceptableOperation("cannot 'popitem()' from the Dict() attribute type!")

    def setdefault(self, key, default=None):
        if key not in self.c.columns:
            raise KeyError(key)
        return super(ValueMatrixRow, self).__getitem__(key)

    def update(self, **kwargs):
        for k in kwargs:
            self.__setitem__(k, kwargs[k])


class ValueMatrix(ValueDict):
    def __init__(self):
        super(ValueMatrix, self).__init__()
        self._objects = dict()
        self._original_values = dict()
        self._values = dict()

    def __repr__(self):
        return "Matrix(%r)" % self._values

    def _matrixrow_from_object(self, obj):
        c = self._get_c()
        row = ValueMatrixRow()
        row.obj = obj
        row.instance = self.instance
        row.model_k = self.model_k
        row.c = c
        for k in c.columns:
            row[k] = getattr(obj, k)
        return row

    def load(self):
        from ..funcs import where_
        c = self._get_c()
        if c is None or self.instance is None:
            return
        self._loaded = True
        model = self.instance.__class__
        session = manager.get_session(instance=self.instance)
        pk = model.__meta__.primary_key
        w = list()
        for k in pk:
            w.append(getattr(c.array_model, 'parent_%s' % k) == getattr(self.instance, k))
        objects = session.select(c.array_model).where(where_(*w)).go()
        self._values = dict()
        for o in objects:
            row = self._matrixrow_from_object(o)
            key = getattr(o, '_k_')
            self._values[key] = row
            self._objects[key] = o
        self._original_values = self._values.copy()

    def reset(self):
        self._objects = dict()
        self._to_delete = list()
        self._values = dict()
        self._loaded = False

    def get(self, key, default=None):
        self.ensure()
        return default if key not in self._values else self._values[key]

    def set(self, key, value):
        if not isinstance(value, dict):
            raise OrmValueError("Matrix attribute requires (dict) type to be given when setting a whole row!")
        self.ensure()
        if key in self._values:
            obj = self._objects[key]
            for k in value:
                if k not in self._get_c().column:
                    raise KeyError("matrix attribute has no column '%s'!" % k)
                setattr(obj, k, value[k])
        else:
            c = self._get_c()
            if c is None:
                raise OrmNotDefinedYet("cannot access values of Matrix until model been defined!")
            obj = self.c.array_model()
            self._assign_with_instance(obj)
            obj._k_ = key
            for k in value:
                if k not in self._get_c().columns:
                    raise KeyError("matrix attribute has no column '%s'!" % k)
                setattr(obj, k, value[k])
            self._objects[key] = obj
        self._values[key] = self._matrixrow_from_object(obj)
        self._verify_changes()

    def has(self, key):
        self.ensure()
        return key in self._values

    def delete(self, key):
        self.ensure()
        if key not in self._values:
            raise KeyError(key)
        obj = self._objects[key]
        self._to_delete.append(obj)
        del (self._objects[key])
        del (self._values[key])
        self._verify_changes()

    def __contains__(self, key):
        return self.has(key)

    def __delitem__(self, key):
        self.delete(key)

    def __getitem__(self, key):
        return self.get(key)

    def __iter__(self):
        self.ensure()
        for k in self._values:
            yield k

    def __len__(self):
        self.ensure()
        return 0 if self._values is None else len(self._values)

    def __setitem__(self, key, value):
        self.set(key, value)

    def clear(self):
        self.ensure()
        keys = self._values.keys()
        for k in keys:
            self.delete(k)

    def copy(self):
        self.ensure()
        return self._values.copy()

    def has_key(self, key):
        self.ensure()
        return self.has(key)

    def items(self):
        self.ensure()
        return self._values.items()

    def keys(self):
        self.ensure()
        return self._values.keys()

    def pop(self, key, default=None):
        raise OrmUnacceptableOperation("cannot 'pop()' from the Matrix() attribute type!")

    def popitem(self):
        raise OrmUnacceptableOperation("cannot 'popitem()' from the Matrix() attribute type!")

    def setdefault(self, key, default=None):
        self.ensure()
        if not self.has(key):
            self.set(key, default)
        return self.get(key)

    def update(self, **kwargs):
        self.ensure()
        for k in kwargs:
            v = kwargs[k]
            self.set(k, v)

    def values(self):
        self.ensure()
        return self._values.values()


class ValueSet(ValueArrayAbstract, set):
    def __init__(self):
        super(ValueSet, self).__init__()
        self._objects = list()
        self._original_values = set()
        self._values = set()

    def __repr__(self):
        return "Set(%r)" % sorted(list(self._values))

    def reset(self):
        self._objects = list()
        self._loaded = False
        self._values = set()

    def write(self):
        dbobjs = self._load_from_db()
        found = list()
        deleted = list()
        for o in dbobjs:
            opt = o.value
            if opt in found or opt not in self._values:
                o.delete()
                deleted.append(o)
                continue
            found.append(opt)
        for o in self._objects:
            opt = o.value
            if opt not in self._values or opt in found:
                continue
            o.write()

    def _load_from_db(self):
        from ..funcs import where_
        c = self._get_c()
        if c is None or self.instance is None:
            return
        model = self.instance.__class__
        session = manager.get_session(instance=self.instance)
        pk = model.__meta__.primary_key
        w = list()
        for k in pk:
            w.append(getattr(c.array_model, 'parent_%s' % k) == getattr(self.instance, k))
        return session.select(c.array_model).where(where_(*w)).go()

    def load(self):
        c = self._get_c()
        if c is None or self.instance is None:
            return
        self._loaded = True
        objects = self._load_from_db()
        self._values = set()
        for o in objects:
            value = getattr(o, 'value')
            self._values.add(value)
            self._objects.append(o)
        self._original_values = set(self._values)

    def __contains__(self, x):
        self.ensure()
        x = str(x)
        return x in self._values

    def __iter__(self):
        self.ensure()
        for x in self._values:
            yield x

    def __len__(self):
        self.ensure()
        return 0 if self._values is None else len(self._values)

    def _ensure_obj(self, x):
        self.ensure()
        x = str(x)
        if x not in self.c.options:
            raise OrmParameterError("value '%s' is not in options list for this Set!" % x)
        for o in self._objects:
            if o.value == x:
                return
        obj = self.c.array_model()
        self._assign_with_instance(obj)
        obj.value = x
        self._objects.append(obj)

    def add(self, x):
        self.ensure()
        c = self._get_c()
        if c is None:
            raise OrmNotDefinedYet("cannot access values of Set until model been defined!")
        x = str(x)
        if x in self._values:
            return
        self._ensure_obj(x)
        self._values.add(x)
        self._verify_changes()

    def remove(self, x):
        self.ensure()
        x = str(x)
        if x not in self._values:
            raise KeyError(x)
        self._values.remove(x)
        self._verify_changes()

    def discard(self, x):
        self.ensure()
        x = str(x)
        if x not in self._values:
            return
        self._values.remove(x)
        self._verify_changes()

    def clear(self):
        self.ensure()
        self._values = set()
        self._verify_changes()

    def copy(self):
        self.ensure()
        return self._values.copy()

    def difference(self, s):
        self.ensure()
        return self._values.difference(set(str(x) for x in s))

    def difference_update(self, s):
        self.ensure()
        for x in s:
            if str(x) not in self._values:
                continue
            self.remove(x)
        return self

    def intersection(self, s):
        self.ensure()
        return self._values.intersection(set(str(x) for x in s))

    def intersection_update(self, s):
        self.ensure()
        for x in self._values:
            if str(x) not in s:
                continue
            self.remove(x)
        return self

    def isdisjoint(self, s):
        self.ensure()
        return self._values.isdisjoint(set(str(x) for x in s))

    def issubset(self, s):
        self.ensure()
        return self._values.issubset(set(str(x) for x in s))

    def issuperset(self, s):
        self.ensure()
        return self._values.issuperset(set(str(x) for x in s))

    def pop(self):
        raise OrmUnacceptableOperation("cannot 'pop()' from the Set() attribute type!")

    def symmetric_difference(self, s):
        self.ensure()
        return self._values.symmetric_difference(set(str(x) for x in s))

    def symmetric_difference_update(self, s):
        self.ensure()
        s_ = self._values.copy()
        for x in self._values:
            if not(str(x) in s and str(x) in s_):
                continue
            self.remove(x)
        for x in s:
            if str(x) in s and str(x) in s_:
                continue
            self.add(str(x))
        return self

    def union(self, s):
        self.ensure()
        for x in s:
            if str(x) in self._values:
                continue
            self.add(str(x))

    def update(self, s):
        self.ensure()
        for x in s:
            self.add(x)


class ValueInlineSet(AttributeValueVirtual, set):
    basecls = False
    check_modified = True

    def __init__(self, value):
        super(ValueInlineSet, self).__init__()
        if value is None:
            value = set()
        elif isinstance(value, str):
            value = self._from_text(value)
        self._value = value
        self._original_value = self._value

    def _get_c(self):
        return getattr(self.instance.__class__, self.model_k) if self.model_k is not None else None

    def _verify_changes(self):
        if self._original_value == self._value and self.model_k in self.instance.__changes__:
            del(self.instance.__changes__[self.model_k])
        elif self._original_value != self._value:
            self.instance.__changes__[self.model_k] = (self._original_value, self._value)

    def __repr__(self):
        return "InlineSet(%r)" % sorted(list(self._value))

    @staticmethod
    def _to_text(value):
        return json.dumps(list(value))

    @staticmethod
    def _from_text(value):
        return set(json.loads(value))

    def base(self, value):
        return self._value

    @property
    def value(self):
        return self._value

    @property
    def dbvalue(self):
        return self._to_text(self._value)

    @property
    def string(self):
        return self.__repr__()

    def get_value(self):
        return self

    def set_value(self, instance, key, value):
        before_ = self._value
        if isinstance(value, ValueInlineSet):
            self._value = value.value
            return self._value, before_
        if value is None or isinstance(value, AttributeValueNull):
            self._value = set()
            return self._value, before_
        if isinstance(value, (set, frozenset, list, tuple)):
            self._value = set(value)
            return self._value, before_
        self._value = set()
        self._value.add(str(value))
        return self._value, before_

    def __contains__(self, x):
        x = str(x)
        return x in self._value

    def __iter__(self):
        for x in self._value:
            yield x

    def __len__(self):
        return 0 if self._value is None else len(self._value)

    def add(self, x):
        c = self._get_c()
        if c is None:
            raise OrmNotDefinedYet("cannot access values of InlineSet until model been defined!")
        x = str(x)
        if x not in self.c.options:
            raise OrmParameterError("value '%s' is not in options list for this Set!" % x)
        if x in self._value:
            return
        self._value.add(x)
        self._verify_changes()

    def remove(self, x):
        x = str(x)
        if x not in self._value:
            raise KeyError(x)
        self._value.remove(x)
        self._verify_changes()

    def discard(self, x):
        x = str(x)
        if x not in self._value:
            return
        self._value.remove(x)

    def clear(self):
        self._value = set()
        self._verify_changes()

    def copy(self):
        return self._value.copy()

    def difference(self, s):
        return self._value.difference(set(str(x) for x in s))

    def difference_update(self, s):
        for x in s:
            if str(x) not in self._value:
                continue
            self.remove(x)
        self._verify_changes()
        return self

    def intersection(self, s):
        return self._value.intersection(set(str(x) for x in s))

    def intersection_update(self, s):
        for x in self._value:
            if str(x) not in s:
                continue
            self.remove(x)
        self._verify_changes()
        return self

    def isdisjoint(self, s):
        return self._value.isdisjoint(set(str(x) for x in s))

    def issubset(self, s):
        return self._value.issubset(set(str(x) for x in s))

    def issuperset(self, s):
        return self._value.issuperset(set(str(x) for x in s))

    def pop(self):
        return self._value.pop()

    def symmetric_difference(self, s):
        return self._value.symmetric_difference(set(str(x) for x in s))

    def symmetric_difference_update(self, s):
        s_ = self._value.copy()
        for x in self._value:
            if not(str(x) in s and str(x) in s_):
                continue
            self.remove(x)
        for x in s:
            if str(x) in s and str(x) in s_:
                continue
            self.add(str(x))
        self._verify_changes()
        return self

    def union(self, s):
        for x in s:
            if str(x) in self._value:
                continue
            self.add(str(x))
        self._verify_changes()

    def update(self, s):
        for x in s:
            self.add(x)
        self._verify_changes()


class ValueAttachmentsAbstract(ValueArrayAbstract, list):
    def __init__(self):
        super(ValueAttachmentsAbstract, self).__init__()
        self._objects = list()
        self._original_values = list()
        self._values = list()

    def __repr__(self):
        return "Attachments(%r)" % self._values

    def reset(self):
        self._objects = list()
        self._to_delete = list()
        self._loaded = False
        self._values = list()

    def write(self):
        super(ValueAttachmentsAbstract, self).write()

    def _assign_with_instance(self, obj):
        super(ValueAttachmentsAbstract, self)._assign_with_instance(obj)
        obj.attachment.parent_instance = self.instance
        obj.attachment.parent_k = self.model_k

    def load(self):
        from ..funcs import where_
        c = self._get_c()
        if c is None or self.instance is None:
            return
        self._loaded = True
        model = self.instance.__class__
        session = manager.get_session(instance=self.instance)
        pk = model.__meta__.primary_key
        w = list()
        for k in pk:
            w.append(getattr(c.array_model, 'parent_%s' % k) == getattr(self.instance, k))
        objects = session.select(c.array_model).where(where_(*w)).order_by(c.array_model.time_created).go()
        self._values = list()
        for o in objects:
            o.attachment.parent_instance = self.instance
            o.attachment.parent_k = self.model_k
            o.attachment.attribute_instance = o
            o.attachment.verify_storage_existance()
            if not o.attachment.is_attached:
                self._to_delete.append(o)
                continue
            self._values.append(o.attachment.filename)
            self._objects.append(o)
        self._original_values = list(self._values)

    def after_parent_instance_deleted(self):
        self.clear()
        self.write()

    def __contains__(self, x):
        self.ensure()
        return x in self._values

    def __delitem__(self, i):
        self.delete_file(i)

    def __delslice__(self, i, j):
        # TODO !
        pass

    def __getitem__(self, i):
        self.ensure()
        if i >= len(self._values):
            raise IndexError(i)
        return self._objects[i]

    def __getslice__(self, i, j):
        # TODO !
        pass

    def __iter__(self):
        self.ensure()
        for x in self._objects:
            yield x

    def __len__(self):
        self.ensure()
        return 0 if self._values is None else len(self._values)

    def __reversed__(self):
        raise OrmUnacceptableOperation("cannot reverse the Files|Pictures attribute!")

    def __setitem__(self, i, x):
        raise OrmUnacceptableOperation("cannot set the Files|Pictures attribute by index to the some value!")

    def append(self, x):
        raise OrmUnacceptableOperation("cannot 'append()' to the Files|Pictures attribute!")

    def add_file_from(self, src, filename=None, rule=None, **kwargs):
        self.ensure()
        c = self._get_c()
        if c is None:
            raise OrmNotDefinedYet("cannot access values of Files|Pictures until model been defined!")
        obj = self.c.array_model()
        self._assign_with_instance(obj)
        obj.attachment.push_file(src, filename, rule)
        obj.title = kwargs.pop('title', filename or obj.attachment.filename)
        obj.filesize = int(math.ceil(float(os.stat(obj.attachment.abs_path).st_size) / 1024.0))
        for k in kwargs:
            setattr(obj, k, kwargs[k])
        self._objects.append(obj)
        self._values.append(obj.attachment.filename)
        self._verify_changes()
        return obj

    def get_file_to(self, i, dst, rule=None):
        self.ensure()
        if isinstance(i, int) and i >= len(self._values):
            raise IndexError(i)
        elif isinstance(i, str):
            if i not in self._values:
                raise KeyError(i)
            i = self._values.index(i)
        elif not isinstance(i, (int, str)):
            raise OrmParameterError("must be (int|str) type!")
        self._objects[i].attachment.pull_file(dst, rule)

    def delete_file(self, i):
        self.ensure()
        if isinstance(i, int) and i >= len(self._values):
            raise IndexError(i)
        elif isinstance(i, str):
            if i not in self._values:
                raise KeyError(i)
            i = self._values.index(i)
        elif not isinstance(i, (int, str)):
            raise OrmParameterError("must be (int|str) type!")
        obj = self._objects[i]
        self._to_delete.append(obj)
        del (self._values[i])
        del (self._objects[i])
        self._verify_changes()

    def clear(self):
        self.ensure()
        while self.__len__() > 0:
            self.delete_file(0)

    def count(self, x):
        self.ensure()
        return self._values.count(x)

    def extend(self, iterable):
        raise OrmUnacceptableOperation("cannot 'extend()' the Files|Pictures attribute!")

    def index(self, x, start=None, stop=None):
        return self._values.index(x, start, stop)

    def insert(self, i, x):
        raise OrmUnacceptableOperation("cannot 'insert()' the Files|Pictures attribute!")

    def pop(self, i: int = -1):
        raise OrmUnacceptableOperation("cannot 'pop()' from the Files|Pictures!")

    def reverse(self):
        raise OrmUnacceptableOperation("cannot 'reverse()' the Files|Pictures!")

    def sort(self, cmp=None, key=None, reverse=False):
        raise OrmUnacceptableOperation("cannot 'sort()' the Files|Pictures attribute!")


class ValueFiles(ValueAttachmentsAbstract):
    def __init__(self):
        super(ValueFiles, self).__init__()

    def __repr__(self):
        return "Files(%r)" % self._values


class ValuePictures(ValueAttachmentsAbstract):
    def __init__(self):
        super(ValuePictures, self).__init__()

    def __repr__(self):
        return "Pictures(%r)" % self._values

    def add_image(self, image, filename=None, **kwargs):
        self.ensure()
        c = self._get_c()
        if c is None:
            raise OrmNotDefinedYet("cannot access values of Files|Pictures until model been defined!")
        obj = self.c.array_model()
        self._assign_with_instance(obj)
        obj.attachment.push_image(image, filename, **kwargs)
        obj.title = kwargs.pop('title', filename or obj.attachment.filename)
        obj.filesize = None
        for k in kwargs:
            setattr(obj, k, kwargs[k])
        self._objects.append(obj)
        self._values.append(obj.attachment.filename)
        self._verify_changes()
        return obj

    def add_image_from(self, src, filename=None, **kwargs):
        self.ensure()
        c = self._get_c()
        if c is None:
            raise OrmNotDefinedYet("cannot access values of Files|Pictures until model been defined!")
        obj = self.c.array_model()
        self._assign_with_instance(obj)
        obj.attachment.push_image_from(src, filename, **kwargs)
        obj.title = kwargs.pop('title', filename or obj.attachment.filename)
        obj.filesize = int(math.ceil(float(os.stat(obj.attachment.abs_path).st_size) / 1024.0))
        for k in kwargs:
            setattr(obj, k, kwargs[k])
        self._objects.append(obj)
        self._values.append(obj.attachment.filename)
        self._verify_changes()
        return obj

    def get_image_to(self, i, dst):
        self.ensure()
        if isinstance(i, int) and i >= len(self._values):
            raise IndexError(i)
        elif isinstance(i, str):
            if i not in self._values:
                raise KeyError(i)
            i = self._values.index(i)
        elif not isinstance(i, (int, str)):
            raise OrmParameterError("must be (int|str) type!")
        self._objects[i].attachment.pull_image_to(dst)

    def get_image(self, i):
        self.ensure()
        if isinstance(i, int) and i >= len(self._values):
            raise IndexError(i)
        elif isinstance(i, str):
            if i not in self._values:
                raise KeyError(i)
            i = self._values.index(i)
        elif not isinstance(i, (int, str)):
            raise OrmParameterError("must be (int|str) type!")
        self._objects[i].attachment.pull_image()

    def delete_image(self, i):
        self.delete_file(i)
