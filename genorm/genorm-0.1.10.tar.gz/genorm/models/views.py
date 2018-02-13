# -*- coding: utf8 -*-
from pc23 import metaclass
from .meta import OrmViewMeta
from ..funcs import and_, where_, having_, RequestOrderBy, RequestGroupBy


@metaclass(OrmViewMeta)
class OrmView(object):
    @classmethod
    def __attrsdir__(cls):
        keys = cls.__attrs__
        attrs = list()
        for k in keys:
            c = getattr(cls, k)
            attrs.append((c.declaration_order, k))
        return [y[1] for y in sorted(attrs, key=lambda x: x[0])]

    @classmethod
    def _get_where(cls):
        def_grnd = getattr(cls, '__where__', None)
        def_attr = getattr(cls, 'where', None)
        if not def_grnd and not def_attr:
            return None
        r = list()
        if def_grnd:
            r.append(def_grnd)
        if def_attr:
            r.append(def_attr)
        return r if len(r) == 1 else and_(*r)

    @classmethod
    def _get_having(cls):
        def_grnd = getattr(cls, '__having__', None)
        def_attr = getattr(cls, 'having', None)
        if not def_grnd and not def_attr:
            return None
        r = list()
        if def_grnd:
            r.append(def_grnd)
        if def_attr:
            r.append(def_attr)
        return r if len(r) == 1 else and_(*r)

    @classmethod
    def _get_order(cls):
        def_grnd = getattr(cls, '__order__', None)
        def_attr = getattr(cls, 'order', None)
        if not def_grnd and not def_attr:
            return None
        r = def_attr if def_attr else def_grnd
        if isinstance(r, RequestOrderBy):
            return [r, ]
        if not isinstance(r, (list, tuple)):
            return [RequestOrderBy(r), ]
        rr = list()
        for r_ in r:
            rr.append(RequestOrderBy(*r_) if isinstance(r_, (list, tuple)) else RequestOrderBy(r_))
        return rr

    @classmethod
    def _get_group(cls):
        def_grnd = getattr(cls, '__group__', None)
        def_attr = getattr(cls, 'group', None)
        if not def_grnd and not def_attr:
            return None
        r = def_attr if def_attr else def_grnd
        if isinstance(r, RequestGroupBy):
            return [r, ]
        if not isinstance(r, (list, tuple)):
            return [RequestGroupBy(r), ]
        rr = list()
        for r_ in r:
            rr.append(RequestGroupBy(*r_) if isinstance(r_, (list, tuple)) else RequestGroupBy(r_))
        return rr

    @classmethod
    def _request_skeleton(cls, *args):
        from ..funcs import left_join_, t_
        from ..attributes.base import AttributeAbstract
        model = getattr(cls, '__model__')
        attrs_unsorted = getattr(cls, '__attrs__')
        joins_unsorted = getattr(cls, '__joins__')
        attrs = list()
        joins = list()
        for k in attrs_unsorted:
            c = getattr(cls, k)
            attrs.append((c.declaration_order, k))
        for k in joins_unsorted:
            c = getattr(cls, k)
            joins.append((c.declaration_order, k))
        attrs = [y[1] for y in sorted(attrs, key=lambda x: x[0])]
        joins = [y[1] for y in sorted(joins, key=lambda x: x[0])]

        _args = list()
        _args.append(model)
        for k in attrs:
            c = getattr(cls, k)
            if c.func is not None:
                _args.append(c.func.as_(k))
            elif c.owner == model.__name__ or c.owner is None:
                _args.append(getattr(model, c.owner_k).as_(k))
            elif c.owner in joins:
                _args.append(getattr(t_(c.owner), c.owner_k).as_(k))
            else:
                continue

        for k in joins:
            c = getattr(cls, k)
            jargs = list()
            for ja in c.args:
                if isinstance(ja.item, AttributeAbstract) and ja.item.model == c.ref_model:
                    ja.item = getattr(t_(k), ja.item.model_k)
                if isinstance(ja.value, AttributeAbstract) and ja.value.model == c.ref_model:
                    ja.value = getattr(t_(k), ja.value.model_k)
                jargs.append(ja)
            _args.append(left_join_(c.ref_model.as_(k), *jargs))

        where = cls._get_where()
        if where:
            _args.append(where_(*where))
        having = cls._get_having()
        if having:
            _args.append(having_(*having))
        order = cls._get_order()
        if order:
            for o in order:
                _args.append(o)
        group = cls._get_group()
        if group:
            for o in group:
                _args.append(o)

        for arg in args:
            _args.append(arg)
        return _args

    @classmethod
    def get(cls, *args, **kwargs):
        return cls.request(*args, **kwargs).go()

    @classmethod
    def find(cls, what, **kwargs):
        from ..request import OrmSearchRequest
        _args = cls._request_skeleton()
        _args.insert(1, what)
        return OrmSearchRequest(*_args, **kwargs)

    @classmethod
    def request(cls, *args, **kwargs):
        from ..request import OrmSelectRequest
        return OrmSelectRequest(*cls._request_skeleton(*args), **kwargs)

