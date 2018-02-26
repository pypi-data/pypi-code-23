from pc23 import xrange
from collections import OrderedDict
from .exceptions import OrmModelClassMismatch, OrmParameterError, OrmInstanceNotFound
from .utils import gettext


class OrmRawResult(object):
    """ Special class which generates by raw query and having the results DBMS returned """
    def __init__(self, cr):
        self.cr = cr
        self._result = self.cr.fetchall()

    def all(self):
        """Return all got from DBMS rows as list of rows of _attrs ([[],[],[]], [[],[],[]]...] """
        return self._result

    def one(self):
        """Return only first row got from DBMS as list of _attrs ([],[],[]...) """
        return self._result[0] if self._result else None

    def __len__(self):
        """ Return quantity of rows in the result """
        return len(self._result)


class OrmResult(tuple):
    def __init__(self):
        super(OrmResult, self).__init__()
        self._total_qty = None
        self.objects = list()
        self.session = None
        self.request = None
        self.page = None
        self.per_page = None
        self.query = None
        self.params = None
        self.rows = None
        self._initialized = True

    def __getitem__(self, item):
        return self.objects[item]

    def __contains__(self, item):
        return item in self.objects

    def __iter__(self):
        for x in self.objects:
            yield x

    def __len__(self):
        return len(self.objects)

    def __repr__(self):
        return self.objects.__repr__()

    def __reversed__(self):
        return self.objects.__reversed__()

    def write(self, session=None, force=False):
        if not self.objects:
            return self
        for instance in self.objects:
            instance.write(session=session, force=force)
        return self

    @property
    def total_qty(self):
        if self._total_qty:
            return self._total_qty
        self._total_qty = self.request.count()
        return self._total_qty

    def one(self, x=None):
        return None if not self.objects else (self.objects[0] if x is None else self.objects[x])

    @property
    def first(self):
        return self.one(0)

    @property
    def last(self):
        return self.one(-1)

    @property
    def sole(self):
        return self.first

    def set(self, **kwargs):
        for instance in self.objects:
            for k in kwargs:
                setattr(instance, k, kwargs[k])
        return self

    def delete(self):
        for instance in self.objects:
            instance.delete()
        return self

    def describe(self):
        if not self.objects:
            return "<None objects>"
        r = list()
        for instance in self.objects:
            r.append(instance.describe())
        return "\n\n-----\n\n".join(r)

    # def __setattr__(self, key, value):
    #     if key.startswith('__') and key.endswith('__'):
    #         super(OrmResult, self).__setattr__(key, value)
    #         return
    #     if key in dir(OrmResult) or key in dir(self):
    #         super(OrmResult, self).__setattr__(key, value)
    #         return
    #     if not getattr(self, '_initialized', False):
    #         super(OrmResult, self).__setattr__(key, value)
    #         return
    #     for instance in self.objects:
    #         setattr(instance, key, value)


class OrmRelatedObjectNotAssigned(object):
    def __init__(self, parent_instance, relation_c):
        self.__parent_instance__ = parent_instance
        self.__relation_c__ = relation_c
        self.__parent_k__ = None

    def __nonzero__(self):
        return False

    def __bool__(self):
        return False

    def __getattribute__(self, key):
        if key in dir(OrmRelatedObjectNotAssigned):
            return super(OrmRelatedObjectNotAssigned, self).__getattribute__(key)
        if key in dir(self):
            return super(OrmRelatedObjectNotAssigned, self).__getattribute__(key)
        child = self.create()
        return child.__getattribute__(key)

    def __setattr__(self, key, value):
        if key in ('__parent_instance__', '__relation_c__', '__parent_k__'):
            super(OrmRelatedObjectNotAssigned, self).__setattr__(key, value)
            return
        child = self.create()
        child.__setattr__(key, value)

    def create(self):
        rel_c = self.__relation_c__
        model = rel_c.ref_model if rel_c.model == self.__parent_instance__.__class__ else rel_c.model
        child = model()
        return self.assign_to(child)

    def assign_to(self, child):
        child.__setattrabs__('__parent__', (self.__parent_instance__, self.__relation_c__))
        setattr(self.__parent_instance__, self.__parent_k__, child)
        return child


class OrmResultOneToMany(OrmResult):
    def __init__(self, src):
        super(OrmResultOneToMany, self).__init__()
        self.objects = list(src.objects)
        self.session = src.session
        self.request = src.request
        self.page = src.page
        self.per_page = src.per_page
        self.query = src.query
        self.params = src.params
        self.rows = src.rows
        self.base_model = None
        self.parent_instance = None
        self.relation_c = None
        self.model = None
        self._to_delete = list()

    def __detach__(self, x):
        y = None
        if isinstance(x, int):
            if x > len(self.objects):
                raise IndexError("object instance's index out of range")
            y = x
        else:
            for i in xrange(len(self.objects)):
                if self.objects[i] != x:
                    continue
                y = i
                break
        if y is None:
            return
        del(self.objects[y])

    def _flag_modified(self):
        pass

    def add(self, x=None, **kwargs):
        from .models.meta import OrmModelMeta
        from .models.base import OrmModelAbstract
        from .attributes.relationships import RelatedToManyAbstract
        if x and isinstance(x, (OrmModelMeta, OrmModelAbstract)):
            if x.__class__ != self.model.__class__:
                raise OrmModelClassMismatch(
                    "Appending object instance has class `%s` while requred `%s`!" %
                    (x.__class__.__name__, self.model.__class__.__name__)
                )
            self.objects.append(x)
            x.__setattrabs__('__parent__', (self.parent_instance, self.relation_c))
            self._flag_modified()
            return
        instance = self.model()
        if kwargs:
            for k in kwargs:
                value = kwargs[k]
                c = getattr(self.model, k)
                if isinstance(value, (list, tuple)) and isinstance(c, RelatedToManyAbstract):
                    childs = getattr(instance, k)
                    for ci in value:
                        if not isinstance(ci, dict):
                            raise OrmParameterError(
                                "childs values must be a type of list of dict!"
                            )
                        childs.add(**ci)
                    continue
                setattr(instance, k, value)
        self.objects.append(instance)
        instance.__setattrabs__('__parent__', (self.parent_instance, self.relation_c))
        self._flag_modified()

    def remove(self, x):
        if x > len(self.objects):
            raise IndexError("object instance's index out of range")
        instance = self.objects[x]
        self._to_delete.append(instance)
        del(self.objects[x])
        self._flag_modified()

    def reverse(self):
        self.objects.reverse()

    def sort(self, attribute, reverse=False, textual=True):
        # TODO!
        if not self.objects:
            return

    def write(self, session=None, force=False):
        for instance in self._to_delete:
            instance.delete()
        self._to_delete = list()
        super(OrmResultOneToMany, self).write(session=session, force=force)


class OrmResultManyToMany(OrmResult):
    def __init__(self, src):
        super(OrmResultManyToMany, self).__init__()
        self.objects = list(src.objects)
        self.session = src.session
        self.request = src.request
        self.page = src.page
        self.per_page = src.per_page
        self.query = src.query
        self.params = src.params
        self.rows = src.rows
        self.base_model = None
        self.parent_instance = None
        self.relation_c = None
        self.local_model = None
        self.ref_model = None
        self.local_model_name = None
        self.ref_model_name = None
        self.junction_model = None
        self.m2m_key = None
        self._to_delete = list()
        self._local_pks = None
        self._assigned = dict()
        self._init_assigned()

    def _init_assigned(self):
        for instance in self.objects:
            pks = self._get_foreign_pks(instance)
            self._assigned[instance] = pks
            self._set_instance_m2m(instance)

    def _find_by_instance(self, f_instance):
        foreign_pks = self._get_foreign_pks(f_instance)
        return self._find_by_pks(foreign_pks)

    def _find_by_pks(self, foreign_pks):
        for fi in self._assigned:
            fpks = self._get_foreign_pks(fi)
            if fpks == foreign_pks:
                return fi
        return None

    def _get_local_pks(self):
        if self._local_pks is not None:
            return self._local_pks
        pks = OrderedDict()
        for c in self.parent_instance.__meta__.get_primary_key():
            k = c.model_k
            v = self.parent_instance.__getattrabs__(k)
            pks[k] = v
        self._local_pks = pks
        return pks

    @staticmethod
    def _get_foreign_pks(f_instance):
        pks = OrderedDict()
        for c in f_instance.__class__.__meta__.get_primary_key():
            k = c.model_k
            v = f_instance.__getattrabs__(k)
            pks[k] = v
        return pks

    def _get_index_of_instance(self, instance):
        return self.objects.index(instance) if instance in self.objects else None

    def _set_instance_m2m(self, instance):
        instance.__m2m__.add(self)

    def _drop_instance_m2m(self, instance):
        instance.__m2m__.discard(self)

    def _assign(self, instance):
        if self._find_by_instance(instance):
            self._set_instance_m2m(instance)
            return
        self.objects.append(instance)
        self._set_instance_m2m(instance)

    def _remove(self, x):
        from .models.meta import OrmModelMeta
        from .models.base import OrmModelAbstract
        if isinstance(x, int):
            if x > len(self.objects):
                raise IndexError("out of range in Many-To-Many relationship for index %i!" % x)
            instance = self.objects[x]
        elif isinstance(x, dict):
            instance = self._find_by_pks(x)
            if not instance:
                raise IndexError("instance with given primary key values is not assigned with this Many-To-Many!")
        elif isinstance(x, (OrmModelMeta, OrmModelAbstract)):
            instance = x
        else:
            raise OrmParameterError(
                "Many-To-Many requires list index, instance or primary key values to be given for deletion!"
            )
        x = self._get_index_of_instance(instance)
        if x is None:
            raise IndexError("given assigned object instance is not found for this Many-To-Many!")
        del(self.objects[x])
        self._drop_instance_m2m(instance)

    def _flag_modified(self):
        self.parent_instance.__set_modified__(self.relation_c.model_k, gettext('Changed'), None)

    def is_assigned(self, f_instance):
        """ Verifies is the given instance already being assigned. """
        return self._find_by_instance(f_instance) is not None

    def find(self, *args, **kwargs):
        """ Tries to find given instance in the list of assigned instance objects by instance
        or by primary key value. Return found object instance if found, None otherwise. """
        if args and len(args) > 1:
            raise OrmParameterError("`ManyToMany`.`find` method requires only ONE instance to be given to find!")
        instance = args[0] if args else None
        if instance is not None:
            return self._find_by_instance(instance)
        elif kwargs:
            return self._find_by_pks(kwargs)
        else:
            raise OrmParameterError(
                "`ManyToMany`.`find` method requires an instance or a primary key values to be given to"
                " find in the junction!"
            )

    def add(self, *args, **kwargs):
        if args and kwargs:
            raise OrmParameterError(
                "`ManyToMany`.`add` requires a foreign instance(s) OR primary key value to be given, but both"
                " instance(s) and primary key value specified instead!"
            )
        elif not args and not kwargs:
            raise OrmParameterError(
                "`ManyToMany`.`add` requires a foreign instance(s) or primary key value to be given, but none"
                " is given!"
            )
        if args:
            for x in args:
                if not isinstance(x, self.ref_model):
                    raise OrmParameterError(
                        "Appending object instance has class `%s` while requred `%s`!" %
                        (x.__class__.__name__, self.ref_model.__class__.__name__)
                    )
                self._assign(x)
        else:
            instance = self._find_by_pks(kwargs)
            if instance:
                return
            w = list()
            for k in kwargs:
                if not hasattr(self.ref_model, k):
                    raise OrmParameterError("OrmModel `%s` has no attribute named `%s`!" % (self.ref_model_name, k))
                w.append(getattr(self.ref_model, k) == kwargs[k])
            r = self.session.select(self.ref_model).where(*w).limit(1).src(self.ref_model).go().one()
            if not r:
                raise OrmInstanceNotFound("Instance with given conditions has not been found!")
            self._assign(r)
        self._flag_modified()

    def delete(self, *args, **kwargs):
        if not args and not kwargs:
            raise OrmParameterError(
                "`ManyToMany`.`delete` requires object instanc(es) OR list index(es) OR primary key values to be"
                " given, but none of them been specified!"
            )
        elif args and kwargs:
            raise OrmParameterError(
                "`ManyToMany`.`delete` requires object instanc(es) OR list index(es) OR primary key values to be"
                " given, but not all at a time!"
            )
        if args:
            for x in args:
                self._remove(x)
        else:
            self._remove(kwargs)
        self._flag_modified()

    def write(self, session=None, force=False):
        session = session or self.session
        w = list()
        m2m_local = self.junction_model.__m2m_columns__[self.local_model_name]
        m2m_ref = self.junction_model.__m2m_columns__[self.ref_model_name]
        for c in m2m_local:
            parent_k = c.parent_model_k
            parent_value = self.parent_instance.__getforwrite__(parent_k, session)
            w.append(c == parent_value)
        existing = session.select(self.junction_model).where(*w).go()
        for fi in self.objects:
            ref_v = dict()
            do_insert = True
            for c in m2m_ref:
                ref_v[c.model_k] = fi.__getforwrite__(c.parent_model_k, session)
            for ei in existing:
                eq = True
                for k in ref_v:
                    v = ref_v[k]
                    if v != ei.__getforwrite__(k, session):
                        eq = False
                        break
                if eq:
                    do_insert = False
                    break
            if not do_insert:
                continue
            ji = self.junction_model()
            for c in m2m_local:
                setattr(ji, c.model_k, self.parent_instance.__getforwrite__(c.parent_model_k, session))
            for c in m2m_ref:
                setattr(ji, c.model_k, fi.__getforwrite__(c.parent_model_k, session))
            ji.__setattrabs__('__session__', session)
            ji.write()
        for ei in existing:
            ref_v = dict()
            avoid_delete = False
            for c in m2m_ref:
                ref_v[c.parent_model_k] = ei.__getforwrite__(c.model_k, session)
            for fi in self.objects:
                eq = True
                for k in ref_v:
                    v = ref_v[k]
                    if v != fi.__getforwrite__(k, session):
                        eq = False
                        break
                if eq:
                    avoid_delete = True
                    break
            if avoid_delete:
                continue
            ei.delete()


class OrmModelUpdateAction(object):
    def __init__(self, model, session, values):
        self._model = model
        self._session = session
        self._values = values
        self._where = None

    def where(self, *args):
        from .funcs import where_
        self._where = where_(args)
        return self

    def go(self):
        objects = self._model.get(session=self._session) \
            if not self._where \
            else self._model.get(self._where, session=self._session)
        if not objects:
            return
        for obj in objects:
            for k in self._values:
                if not hasattr(obj, k):
                    continue
                setattr(obj, k, self._values[k])
            obj.write()

