from collections import OrderedDict
from pc23 import xrange
from .exceptions import OrmRequestError, OrmAttributeTypeMistake, OrmModelClassMismatch, OrmDefinitionError, \
    OrmParameterError, OrmModelDeclarationError
from .models.meta import OrmModelMeta
from .models.base import OrmModelAbstract, OrmModelAliased, CompositeOrmModel
from .attributes.base import DataAttributeAbstract, AttributeAliased, OrmComparator, ColumnAttributeAbstract, \
    OrmComparatorMixin
from .attributes.columns import ColumnIntegerAbstract, ColumnBooleanAbstract, ColumnDatetimeAbstract
from .attributes.relationships import ForeignAttr
from .funcs import DbFunctionAbstract, RequestWhere, RequestHaving, RequestLimit, RequestOrderBy, \
    RequestGroupBy, RequestNamedColumn, RequestTableBelongedColumn, RequestJoinAbstract, RawSql, left_join_, \
    right_join_, inner_join_, full_join_, t_, or_
from .results import OrmResult
from .manage import manager
from .utils import split_search_phrase

REQUEST_SELECT = 'select'
REQUEST_UPDATE = 'update'
REQUEST_INSERT = 'insert'
REQUEST_REPLACE = 'replace'
REQUEST_DELETE = 'delete'
REQUEST_UNDELETE = 'undelete'


class OrmRequest(object):
    def __init__(self, request_type, *args, **kwargs):
        self._type = request_type.lower()
        self._aliases = set()
        self._aliases_tbl = set()
        self._aliases_col = set()
        self._attrs = dict()
        self._sources = list()
        self._columns = list()
        self._joins = list()
        self._models = OrderedDict()
        self._tbl_aliases = dict()
        self._col_aliases = dict()
        self._where = None
        self._having = None
        self._limit = None
        self._order_by = None
        self._group_by = None
        self._union_order_by = None
        self._union_group_by = None
        self._union_limit = None
        self._is_finished = False
        self._union = None
        self._req_columns = None
        self._req_srcs = list()
        self._src_belongs_to = dict()
        self._c_belongs_to = dict()
        self._requesting_sources = list()
        self._inserted_id = None
        self._resulting_model = None
        self._foreign_attrs = dict()
        self._autojoins = dict()
        self._related_objects = OrderedDict()
        self._related_obj_attrs = list()
        self.session = kwargs.pop('session', None)
        self.params = dict()
        self.ignore = kwargs.pop('ignore', False)
        self.distinct = kwargs.pop('distinct', False)
        self.high_priority = kwargs.pop('high_priority', False)
        self.straight_join = kwargs.pop('straight_join', False)
        self.sql_big_result = kwargs.pop('sql_big_result', False)
        self.sql_small_result = kwargs.pop('sql_small_result', False)
        self.sql_buffer_result = kwargs.pop('sql_buffer_result', False)
        self.sql_calc_found_rows = kwargs.pop('sql_calc_found_rows', False)
        self.sql_cache = kwargs.pop('sql_cache', False)
        self.sql_no_cache = kwargs.pop('sql_no_cache', False) if not self.sql_cache else False
        self.for_update = kwargs.pop('for_update', False)
        self.lock_in_share_mode = kwargs.pop('lock_in_share_mode', False)
        self.deleted = kwargs.pop('with_deleted', False)
        self.values = kwargs.pop('values', None)
        self.hard_delete = bool(kwargs.pop('hard_delete', False))
        self.with_values = kwargs.pop('with_values', None)
        self.with_default = kwargs.pop('with_default', None)
        self.textual_options = bool(kwargs.pop('textual_options', False))
        self.only_own = bool(kwargs.pop('only_own', False))
        if self.values and self._type not in ('update', 'insert', 'replace'):
            raise OrmRequestError("'values' might be set for UPDATE, INSERT or REPLACE requests only!")
        if self._type in ('update', 'insert') and not self.values:
            raise OrmRequestError("'values' must be set for UPDATE, INSERT or REPLACE request!")
        if self.ignore and self._type != 'insert':
            raise OrmRequestError("'ignore' can only be set for INSERT command!")

        for arg in args:
            if isinstance(arg, (OrmModelMeta, OrmModelAbstract, OrmModelAliased)):
                self._add_source(arg)
                self._requesting_sources.append(arg)
            elif isinstance(arg, RequestJoinAbstract):
                self._add_join(arg)
            elif isinstance(arg, (DataAttributeAbstract, DbFunctionAbstract)):
                self._resulting_model = CompositeOrmModel
                self._add_attribute(arg)
            elif isinstance(arg, (AttributeAliased, RequestTableBelongedColumn)):
                self._resulting_model = CompositeOrmModel
                self._add_attribute(arg)
            elif isinstance(arg, OrmComparator):
                self._add_where(arg)
            elif isinstance(arg, RequestWhere):
                self._add_where(arg)
            elif isinstance(arg, RequestHaving):
                self._add_having(arg)
            elif isinstance(arg, RequestLimit):
                self._set_limit(arg)
            elif isinstance(arg, RequestOrderBy):
                self._add_orderby(arg)
            elif isinstance(arg, RequestGroupBy):
                self._add_groupby(arg)
            else:
                raise OrmRequestError(
                    "Unsupported type of argument given for the request of type '%s'!" % str(type(arg))
                )

    def _add_source(self, src):
        if src in self._sources and not isinstance(src, OrmModelAliased):
            raise OrmRequestError(
                "OrmModel must be named using .as_() method if this model should be used several times"
                " it the query!"
            )
        elif src in self._sources:
            raise OrmRequestError(
                "The same OrmModel, with same naming, cannot be specified in the request more than once!"
            )
        if isinstance(src, OrmModelAliased):
            if src.alias in self._aliases:
                raise OrmRequestError("Alias is already defined: '%s'!" % str(src.alias))
            self._register_table_alias(src.alias, src)
        self._sources.append(src)
        self._req_srcs.append(src)

    def _add_join(self, j, belongs_to=None):
        src = j.source
        if src in self._sources and not isinstance(src, OrmModelAliased):
            raise OrmRequestError(
                "OrmModel must be named using .as_() method if this model should be used several times"
                " it the query!"
            )
        elif src in self._sources:
            raise OrmRequestError(
                "The same OrmModel, with same naming, cannot be specified in the request more than once!"
            )
        if isinstance(src, OrmModelAliased):
            if src.alias in self._aliases:
                raise OrmRequestError("Alias is already defined: '%s'!" % str(src.alias))
            self._register_table_alias(src.alias, src)
        self._joins.append(j)
        req_src = belongs_to if belongs_to else j
        if req_src not in self._req_srcs:
            self._req_srcs.append(req_src)

    def _add_attribute(self, c):
        if isinstance(c, ColumnAttributeAbstract) and self._type == 'select':
            k = c.tbl_k or c.model_k
            c = c.make_read(self)
            c.tbl_k = k
            c.model_k = k
        elif isinstance(c, RequestTableBelongedColumn):
            c.make_read(self)
        if isinstance(c, AttributeAliased):
            if c.alias in self._aliases:
                raise OrmRequestError("Alias is already defined: '%s'!" % str(c.alias))
            self._register_column_alias(c.alias, c.c)
        else:
            self._attrs[c] = None
        self._columns.append(c)

    def _add_where(self, *expr):
        for arg in expr:
            if isinstance(arg, RequestWhere):
                arg = arg.args
            if self._where is None:
                self._where = RequestWhere(arg)
            elif isinstance(self._where, RequestWhere):
                self._where.extend_with(arg)
            else:
                raise OrmRequestError(
                    "Unexpected type of value for filter 'WHERE' of the request: %s" % str(type(self._where))
                )

    def _add_having(self, *expr):
        for arg in expr:
            if isinstance(arg, RequestHaving):
                arg = arg.args
            if self._having is None:
                self._having = RequestHaving(arg)
            elif isinstance(self._having, RequestHaving):
                self._having.extend_with(arg)
            else:
                raise OrmRequestError(
                    "Unexpected type of value for filter 'HAVING' of the request: %s" % str(type(self._having))
                )

    def _set_limit(self, arg):
        if self._union is None or self._union is True:
            self._limit = arg
        else:
            self._union_limit = arg

    def _add_orderby(self, arg):
        if self._union is None or self._union is True:
            if self._order_by is None:
                self._order_by = list()
            self._order_by.append(arg)
        else:
            if self._union_order_by is None:
                self._union_order_by = list()
            self._union_order_by.append(arg)

    def _add_groupby(self, arg):
        if self._union is None or self._union is True:
            if self._group_by is None:
                self._group_by = list()
            self._group_by.append(arg)
        else:
            if self._union_group_by is None:
                self._union_group_by = list()
            self._union_group_by.append(arg)

    def _fillup_columns(self):
        if self._col_aliases or self._columns:
            return
        for src in self._models:
            if self._requesting_sources \
                    and not (src in self._requesting_sources
                             or (isinstance(src, OrmModelAliased) and src.alias in self._requesting_sources)):
                continue
            model = src.model if isinstance(src, OrmModelAliased) else src
            attrs = model.__meta__.get_attributes_for_select() \
                if self._type == 'select' \
                else model.__meta__.get_attributes_for_write()
            for c in attrs:
                if issubclass(self.resulting_model, CompositeOrmModel) \
                        and not getattr(c, 'in_composite_results', True):
                    continue
                alias = c.tbl_k or c.model_k
                c_ = RequestTableBelongedColumn(alias, src.alias) if isinstance(src, OrmModelAliased) else c
                self._add_attribute(c_)

    def _register_table_alias(self, alias, model):
        self._aliases.add(alias)
        self._aliases_tbl.add(alias)
        self._tbl_aliases[alias] = model
        self._models[model] = alias

    def _register_column_alias(self, alias, c):
        self._aliases.add(alias)
        self._aliases_col.add(alias)
        self._attrs[c] = alias
        self._col_aliases[alias] = c

    def _get_free_table_alias(self, prefix):
        i = len(self._aliases_tbl)
        n = "%s%i" % (str(prefix), i)
        while n in self._aliases:
            i += 1
            n = "%s%i" % (str(prefix), i)
        return n

    def _get_free_column_alias(self, prefix, c=None):
        if c is not None and isinstance(c, ColumnAttributeAbstract):
            c_src = c.model
            tbl_name = self._models[c_src]
            col_name = c.tbl_k
            col_alias = "%s_%s" % (tbl_name, col_name)
            if col_alias not in self._aliases:
                return col_alias
        elif c is not None and isinstance(c, RequestTableBelongedColumn):
            tbl_name = c.tbl_name
            model = self._tbl_aliases[tbl_name]
            if isinstance(model, OrmModelAliased):
                model = model.model
            k = c.k
            c = getattr(model, k)
            col_name = c.tbl_k
            if col_name:
                col_alias = "%s_%s" % (tbl_name, col_name)
                if col_alias not in self._aliases:
                    return col_alias
        i = len(self._aliases_col) + 1
        n = "%s%i" % (str(prefix), i)
        while n in self._aliases:
            i += 1
            n = "%s%i" % (str(prefix), i)
        return n

    def _name_unnamed_sources(self):
        for src in self._sources:
            if isinstance(src, OrmModelAliased):
                continue
            tbl_alias = self._get_free_table_alias('t')
            self._register_table_alias(tbl_alias, src)
        for j in self._joins:
            if isinstance(j.source, OrmModelAliased):
                continue
            src = j.source
            tbl_alias = self._get_free_table_alias('t')
            self._register_table_alias(tbl_alias, src)

    def _name_unnamed_columns(self):
        for c in self._columns:
            if isinstance(c, AttributeAliased):
                continue
            col_alias = self._get_free_column_alias('c', c)
            self._register_column_alias(col_alias, c)

    def get_valueparam_by_column(self, c):
        if c in self.values:
            value = self.values[c]
        elif isinstance(c, DataAttributeAbstract):
            k = c.model_k
            if k in self.values:
                value = self.values[k]
            else:
                return None
        else:
            return None
        pn = c.model_k if isinstance(c, DataAttributeAbstract) else str(c)
        if not pn:
            return None
        self.params[pn] = value
        return pn

    def _sql_from(self):
        if self._type in ('insert', 'replace') and len(self._sources) != 1:
            raise OrmRequestError("INSERT requests must have ONE OrmModel to be specified!")
        p = list()
        for src in self._sources:
            tbl_alias = src.alias if isinstance(src, OrmModelAliased) else self._models[src]
            tbl_name = src.model.table if isinstance(src, OrmModelAliased) else src.table
            p.append("%s AS %s" % (self.session.quote_name(tbl_name), tbl_alias)
                     if self._type not in ('insert', 'replace', 'update', 'delete')
                     else "%s" % self.session.quote_name(tbl_name))
        return ", ".join(p)

    def _sql_joins(self):
        p = list()
        for j in self._joins:
            src = j.source
            tbl_alias = src.alias if isinstance(src, OrmModelAliased) else self._models[src]
            tbl_name = src.model.table if isinstance(src, OrmModelAliased) else src.table
            join_sql = j.join_type
            j_cond = j.condition
            sql_cond = self.resolve_expr(j_cond)
            f_softdelete = self._source_softdelete_filter(src)
            if f_softdelete:
                sql_softdelete = self.resolve_expr(f_softdelete, allow_alias=False)
                sql_cond = sql_softdelete + " AND " + sql_cond
            p.append("%s %s AS %s ON %s" % (join_sql, self.session.quote_name(tbl_name), tbl_alias, sql_cond))
        return " ".join(p)

    def _sql_sources(self):
        gsrc = list()
        gsrc.append(self._sql_from())
        if self._type in ('insert', 'replace') and self._joins:
            raise OrmRequestError("Cannot use JOINs in the INSERT or REPLACE request!")
        joins = self._sql_joins()
        if joins:
            gsrc.append(joins)
        return " ".join(gsrc)

    def _sql_insert_columns(self):
        self._req_columns = list()
        p = list()
        for c in self._columns:
            q = self.sql_column(c, permit_c=True, permit_f=False)
            qp = self._sql_write_param(c)
            if not qp or not q:
                continue
            p.append(q)
            self._req_columns.append(c)
        if not p:
            return None
        return ", ".join(p)

    def _sql_insert_values(self):
        p = list()
        for c in self._columns:
            q = self.sql_column(c, permit_c=True, permit_f=False)
            if q:
                qp = self._sql_write_param(c)
                if not qp:
                    continue
                p.append(qp)
        if not p:
            return None
        return ", ".join(p)

    def _sql_write_param(self, c):
        c_ = c.make_write(self) if isinstance(c, ColumnAttributeAbstract) else c
        if isinstance(c_, DbFunctionAbstract):
            return c_.resolve(self)
        elif isinstance(c_, ColumnAttributeAbstract):
            return c_.make_write(self)
        return c_

    def _sql_columns(self):
        self._req_columns = list()
        p = list()
        for c in self._columns:
            q = self.sql_column(c, permit_c=True, permit_f=True)
            if q:
                if self._type in ('update', 'insert', 'replace'):
                    qp = self._sql_write_param(c)
                    if not qp:
                        continue
                    q += "=" + qp
                p.append(q)
                self._req_columns.append(c)
        if not p:
            return None
        return ", ".join(p)

    def _sql_where(self):
        if self._where is None:
            return ""
        q_ = self.resolve_expr(self._where.args, allow_alias=False)
        if not q_:
            return ""
        return q_

    def _sql_having(self):
        if self._having is None:
            return ""
        q_ = self.resolve_expr(self._having.args, allow_alias=True)
        if not q_:
            return ""
        return q_

    def _sql_limit(self, value=None):
        value = value or self._limit
        if not value:
            return ""
        if not isinstance(value, RequestLimit):
            raise OrmRequestError("Request._limit must be a type of (RequestLimit)!")
        return "%i OFFSET %i" % (value.limit, value.offset) \
            if value.offset \
            else str(value.limit)

    def _sql_orderby(self):
        if not self._order_by:
            return ""
        p = list()
        for arg in self._order_by:
            if not isinstance(arg, RequestOrderBy):
                raise OrmRequestError("Request._order_by element must be a type of (RequestOrderBy)!")
            c = arg.c
            if isinstance(c, ColumnAttributeAbstract):
                c = c.make_order_by(self)
            p.append("%s %s" % (self._resolve_attr(c, allow_alias=True), arg.d))
        return ", ".join(p)

    def _sql_groupby(self):
        if not self._group_by:
            return ""
        p = list()
        for arg in self._group_by:
            if not isinstance(arg, RequestGroupBy):
                raise OrmRequestError("Request._group_by element must be a type of (RequestGroupBy)!")
            c = arg.c
            if isinstance(c, ColumnAttributeAbstract):
                c = c.make_group_by(self)
            p.append(self._resolve_attr(c, allow_alias=True))
        return ", ".join(p)

    def _sql_union_limit(self, value=None):
        value = value or self._union_limit
        if not value:
            return ""
        if not isinstance(value, RequestLimit):
            raise OrmRequestError("Request._limit must be a type of (RequestLimit)!")
        return "%i OFFSET %i" % (value.limit, value.offset) \
            if value.offset \
            else str(value.limit)

    def _sql_union_orderby(self):
        if not self._union_order_by:
            return ""
        p = list()
        for arg in self._union_order_by:
            if not isinstance(arg, RequestOrderBy):
                raise OrmRequestError("Request._order_by element must be a type of (RequestOrderBy)!")
            c = arg.c
            if isinstance(c, ColumnAttributeAbstract):
                c = c.make_order_by(self)
            p.append("%s %s" % (self._resolve_attr(c, allow_alias=True), arg.d))
        return ", ".join(p)

    def _sql_union_groupby(self):
        if not self._union_group_by:
            return ""
        p = list()
        for arg in self._union_group_by:
            if not isinstance(arg, RequestGroupBy):
                raise OrmRequestError("Request._group_by element must be a type of (RequestGroupBy)!")
            c = arg.c
            if isinstance(c, ColumnAttributeAbstract):
                c = c.make_group_by(self)
            p.append(self._resolve_attr(c, allow_alias=True))
        return ", ".join(p)

    def _resolve_attr(self, item, allow_alias=False, table_name=None):
        if item is None:
            return "NULL"
        elif isinstance(item, (ColumnAttributeAbstract, RequestTableBelongedColumn, DbFunctionAbstract)) \
                and item in self._attrs \
                and allow_alias:
            return str(self._attrs[item])
        elif isinstance(item, AttributeAliased) and allow_alias:
            return item.alias
        elif isinstance(item, ColumnAttributeAbstract):
            c_src = item.model
            tbl_name = self._models[c_src] if not table_name else table_name
            col_name = item.tbl_k
            return "%s.%s" % (self.session.quote_name(tbl_name), self.session.quote_name(col_name)) \
                if self._type not in ('update', 'delete') \
                else self.session.quote_name(col_name)
        elif isinstance(item, RequestTableBelongedColumn):
            k = item.k
            tbl_name = item.tbl_name
            if tbl_name not in self._tbl_aliases:
                raise OrmRequestError(
                    "Table with alias name '%s' is not defined in the request, for column '%s'!" % (tbl_name, k)
                )
            c_model = self._tbl_aliases[tbl_name]
            c_model_ = c_model.model if isinstance(c_model, OrmModelAliased) else c_model
            if not hasattr(c_model_, k):
                raise OrmRequestError(
                    "OrmModel '%s', which is associated with table alias '%s' in the request, has no"
                    " attribute '%s' declared in it!" % (c_model_.__name__, tbl_name, k)
                )
            c_ = getattr(c_model_, k)
            if isinstance(c_, ColumnAttributeAbstract):
                col_name = c_.tbl_k
                return "%s.%s" % (self.session.quote_name(tbl_name), self.session.quote_name(col_name))
            elif isinstance(c_, DbFunctionAbstract):
                return c_.resolve(self, table_name=tbl_name)
            else:
                raise OrmRequestError(
                    "Attribute '%s' of OrmModel '%s', declared in the request with table alias '%s', is"
                    " not a type of (Column|DbFunction) and cannot be queried!" % (k, c_model_.__name__, tbl_name)
                )
        elif isinstance(item, OrmRequest):
            query_ = item.sql
            params_ = item.params
            for k in params_:
                v = params_[k]
                k_ = 'p%i' % len(self.params)
                kf_ = "%(" + k + ")s"
                kt_ = "%(" + k_ + ")s"
                query_ = query_.replace(kf_, kt_)
                self.params[k_] = v
            return "(" + query_ + ")"
        elif isinstance(item, DbFunctionAbstract):
            return item.resolve(self, table_name=table_name)
        elif isinstance(item, RawSql):
            return str(item.value)
        elif isinstance(item, RequestNamedColumn):
            return item.column_name
        pn = "p%i" % len(self.params)
        self.params[pn] = item
        sn = "%(" + pn + ")s"
        return sn

    def resolve_expr(self, expr, allow_alias=False, table_name=None):
        def _true(expr_):
            if isinstance(expr_, ColumnAttributeAbstract):
                return expr_.true_
            return expr_

        def _false(expr_):
            if isinstance(expr_, ColumnAttributeAbstract):
                return expr_.false_
            return "NOT %s" % str(expr_)

        def _is_null(expr_):
            return "%s IS NULL" % expr_

        def _is_not_null(expr_):
            return "%s IS NOT NULL" % expr_

        def _in(expr_, values_, isnot_=False):
            rv_ = list()
            if isinstance(values_, OrmRequest):
                query_ = expr_.sql
                params_ = expr_.params
                for k in params_:
                    v = params_[k]
                    k_ = 'p%i' % len(self.params)
                    kf_ = "%(" + k + ")s"
                    kt_ = "%(" + k_ + ")s"
                    query_ = query_.replace(kf_, kt_)
                    self.params[k_] = v
                rv = query_
            elif isinstance(values_, (list, tuple)):
                if not isinstance(values_, (list, tuple)):
                    values_ = [values_, ]
                for v_ in values_:
                    vq_ = str(v_)
                    pn_ = "p%i" % (len(self.params))
                    rv_.append("%(" + pn_ + ")s")
                    self.params[pn_] = vq_
                rv = ", ".join(rv_)
            elif isinstance(values_, str):
                rv = values_
            else:
                raise OrmRequestError("'IN' and 'NOT IN' must have a (list|tuple) or OrmRequest as parameter!")
            q_not_ = " NOT" if isnot_ else ""
            return str(expr_) + q_not_ + " IN (" + rv + ")"

        def _not_in(expr_, values_):
            return _in(expr_, values_, True)

        def _cmp(expr_, cmp_, value_):
            if value_ is None:
                if cmp_ == '=':
                    return _is_null(expr_)
                elif cmp_ == '!=':
                    return _is_not_null(expr_)
                else:
                    raise OrmRequestError("SQL comparition with NULL may be only 'IS NULL' or 'IS NOT NULL'!")
            elif isinstance(value_, (list, tuple)):
                if cmp_ == '=':
                    return _in(expr_, value_)
                elif cmp_ == '!=':
                    return _not_in(expr_, value_)
                else:
                    raise OrmRequestError("SQL comparition with array may be only 'IN' or 'NOT IN'!")
            return expr_ + " " + cmp_ + " " + value_

        if expr is True or expr is False:
            raise OrmRequestError(
                "Incorrect filter is set. Probably trying to compare non database reflected attributes"
                " with some value. Only database reflected columns (columns, directly pointing to the"
                " corresponding database table columns) can be used in the query filters in ORM."
            )
        if not expr:
            return ""
        if not isinstance(expr, (list, tuple)):
            expr = ['AND', expr, ]
        if isinstance(expr[0], str) and expr[0] not in ('EXISTS', '!EXISTS', 'AND', 'OR'):
            raise OrmRequestError('Incorrect joins condition for filter in query: %s' % expr[0])
        elif not isinstance(expr[0], str):
            expr = ['AND'] + list(expr)
        if expr[0] == 'EXISTS':
            if len(expr) != 2:
                raise OrmRequestError("Incorrect filter with EXISTS modifier!")
            r_ = self.resolve_expr(expr[1], table_name=table_name)
            if not r_:
                return ""
            return "EXISTS(" + r_ + ")"
        elif expr[0] == '!EXISTS':
            if len(expr) != 2:
                raise OrmRequestError("Incorrect filter with NOT EXISTS modifier!")
            r_ = self.resolve_expr(expr[1], table_name=table_name)
            if not r_:
                return ""
            return "NOT EXISTS(" + r_ + ")"
        if expr[0] not in ('AND', 'OR'):
            expr = ['AND'] + list(expr)
        fj_ = " %s " % expr[0]
        fc_ = expr[1:]
        r_ = list()
        for f_ in fc_:
            if not isinstance(f_, (OrmComparator, tuple, list)):
                f_ = OrmComparator(f_, 'TRUE') if not isinstance(f_, OrmComparatorMixin) else f_.true_
            if isinstance(f_, OrmComparator):
                f_ = f_.resolve(self.session)
            if isinstance(f_, OrmComparator):
                item_ = f_.item
                if isinstance(item_, ColumnAttributeAbstract):
                    item_ = item_.make_filter(self)
                item_ = self._resolve_attr(item_, allow_alias=allow_alias, table_name=table_name)
                comparator_ = f_.cmp
                if comparator_ == 'ISNULL':
                    r_.append(_is_null(item_))
                    continue
                elif comparator_ == '!ISNULL':
                    r_.append(_is_not_null(item_))
                    continue
                elif comparator_ == 'TRUE':
                    r_.append(_true(item_))
                    continue
                elif comparator_ == 'FALSE':
                    r_.append(_false(item_))
                    continue
                right_ = f_.value
                if not isinstance(right_, (list, tuple)):
                    right_ = self._resolve_attr(right_, table_name=table_name)
                if comparator_ == 'IN':
                    r_.append(_in(item_, right_))
                    continue
                elif comparator_ == '!IN':
                    r_.append(_not_in(item_, right_))
                    continue
                elif isinstance(right_, (list, tuple)):
                    raise OrmRequestError("Cannot use (list|tuple) for comparators other than IN or NOT IN!")
                else:
                    r_.append(_cmp(item_, comparator_, right_))
            else:
                rf_ = self.resolve_expr(f_, table_name=table_name)
                if rf_:
                    rf_ = ("(" + rf_ + ")") if len(f_) > 1 else rf_
                    r_.append(rf_)
        if not r_:
            return ""
        return str(fj_).join(r_) if len(r_) > 1 else str(r_[0])

    def ensure_column(self, column):
        if isinstance(column, RequestNamedColumn):
            if column.column_name in self._col_aliases:
                raise OrmRequestError("Column is not defined in the request: '%s'!" % column.column_name)
        if column not in self._columns:
            self._add_attribute(column)

    def _handle_sql_column(self, c, *args):
        sql_ = list()
        for arg in args:
            sql_.append(self.session.quote_name(arg))
        sql = ".".join(sql_)
        if not self.textual_options:
            return sql
        options = getattr(c, 'options', None)
        if not options:
            return sql
        if not isinstance(options, dict):
            raise OrmDefinitionError("attribute's 'options' must be a (dict) type!")
        sql_case = list()
        for k in options:
            v = options[k]
            pn_k = "p%i" % len(self.params)
            self.params[pn_k] = k
            pn_v = "p%i" % len(self.params)
            self.params[pn_v] = v
            sql_case.append("WHEN %(" + pn_k + ")s THEN %(" + pn_v + ")s")
        sql = "(CASE " + str(sql) + " " + " ".join(sql_case) + " ELSE " + str(sql) + " END)"
        return sql

    def sql_column(self, c, permit_c=True, permit_f=True, alias=True, table_name=None):
        if self._type in ('insert', 'replace', 'update', 'delete'):
            if not isinstance(c, ColumnAttributeAbstract):
                return None
            return "%s" % self.session.quote_name(c.tbl_k)
        tbl_name = table_name
        if (isinstance(c, ForeignAttr) or (isinstance(c, AttributeAliased) and isinstance(c.c, ForeignAttr))) \
                and self._type == 'select':
            if isinstance(c, AttributeAliased):
                c = c.c
            c.validate()
            rel_obj_k = c.related_k
            rel_model_name = c.model.__name__
            rel_aj_name = "%s_%s" % (rel_model_name, rel_obj_k)
            if rel_aj_name not in self._autojoins:
                return None
            alias_name = self._attrs[c] if c in self._attrs else None
            rel_c = getattr(c.model, rel_obj_k)
            rel_c.validate()
            foreign_model = rel_c.foreign_model
            ref_k = c.referenced_k
            ref_c = getattr(foreign_model, ref_k)
            if not isinstance(ref_c, ColumnAttributeAbstract):
                return None
            col_name = ref_c.tbl_k
            tbl_name = self._autojoins[rel_aj_name]
            return "%s AS %s" % (self._handle_sql_column(rel_c, tbl_name, col_name), alias_name) \
                if alias and alias_name \
                else self._handle_sql_column(rel_c, tbl_name, col_name)
        if isinstance(c, DataAttributeAbstract) and not isinstance(c, ColumnAttributeAbstract):
            return None
        if isinstance(c, RequestNamedColumn):
            return str(c.column_name)
        if isinstance(c, ColumnAttributeAbstract) and not permit_c:
            return None
        if isinstance(c, DataAttributeAbstract):
            c_src = c.model
            tbl_name = self._models[c_src] if not table_name else table_name
            col_name = c.tbl_k
            alias_name = self._attrs[c] if c in self._attrs else None
            return "%s AS %s" % (self._handle_sql_column(c, tbl_name, col_name), alias_name) \
                if alias and alias_name and self._type == 'select' \
                else self._handle_sql_column(c, tbl_name, col_name)
        if isinstance(c, AttributeAliased):
            c_ = c.c
            alias_name = c.alias
        else:
            c_ = c
            alias_name = self._attrs[c] if c in self._attrs else None
        if isinstance(c_, ColumnAttributeAbstract) and permit_c:
            c_src = c_.model
            tbl_name = self._models[c_src] if not table_name else table_name
            col_name = c_.tbl_k
            return "%s AS %s" % (self._handle_sql_column(c_, tbl_name, col_name), alias_name) \
                if alias and alias_name and self._type == 'select' \
                else self._handle_sql_column(c_, tbl_name, col_name)
        if isinstance(c_, RequestTableBelongedColumn):
            k = c_.k
            tbl_name = c_.tbl_name if not table_name else table_name
            if tbl_name not in self._tbl_aliases:
                raise OrmRequestError(
                    "Table with alias name '%s' is not defined in the request, for column '%s'!" % (tbl_name, k)
                )
            c_model = self._tbl_aliases[tbl_name]
            c_model_ = c_model.model if isinstance(c_model, OrmModelAliased) else c_model
            if not hasattr(c_model_, k):
                raise OrmRequestError(
                    "OrmModel '%s', which is associated with table alias '%s' in the request, has no"
                    " attribute '%s' declared in it!" % (c_model_.__name__, tbl_name, k)
                )
            c_ = getattr(c_model_, k) if c_.c is None else c_.c
            if isinstance(c_, ColumnAttributeAbstract) and permit_c:
                col_name = c_.tbl_k
                return "%s AS %s" % (self._handle_sql_column(c_, tbl_name, col_name), alias_name) \
                    if alias and alias_name and self._type == 'select' \
                    else self._handle_sql_column(tbl_name, col_name)
        if isinstance(c_, DbFunctionAbstract) and permit_f:
            expr_sql = c_.resolve(self, table_name=tbl_name)
            return "%s AS %s" % (str(expr_sql), alias_name) \
                if alias and alias_name and self._type == 'select' \
                else str(expr_sql)
        return None

    @staticmethod
    def _source_softdelete_filter(src):
        model = src.model if isinstance(src, OrmModelAliased) else src
        c_softdelete = model.__meta__.soft_delete
        if not c_softdelete:
            return None
        fc_ = getattr(t_(src), c_softdelete.model_k) if isinstance(src, OrmModelAliased) else c_softdelete
        if isinstance(c_softdelete, ColumnBooleanAbstract):
            return fc_.false_
        elif isinstance(c_softdelete, ColumnDatetimeAbstract):
            return fc_.false_
        elif isinstance(c_softdelete, ColumnIntegerAbstract):
            return fc_.notnull_
        else:
            raise OrmAttributeTypeMistake(
                "Soft-delete key might be of type (Boolean|Date|DateTime|Timestamp|Integer) only!"
            )

    def _sql_softdelete_set(self):
        src = self._sources[0]
        model = src.model if isinstance(src, OrmModelAliased) else src
        c_softdelete = model.__meta__.soft_delete
        if not c_softdelete:
            return None
        c_ = getattr(t_(src), c_softdelete.model_k) if isinstance(src, OrmModelAliased) else c_softdelete
        q_ = self.sql_column(c_, permit_c=True, permit_f=False, alias=False)
        if isinstance(c_softdelete, ColumnBooleanAbstract):
            return q_ + "=TRUE"
        elif isinstance(c_softdelete, ColumnDatetimeAbstract):
            return q_ + "=NOW()"
        elif isinstance(c_softdelete, ColumnIntegerAbstract):
            return q_ + "=NULL"
        else:
            raise OrmAttributeTypeMistake(
                "Soft-delete key might be of type (Boolean|Date|DateTime|Timestamp|Integer) only!"
            )

    def _handle_softdelete_select(self):
        if self.deleted or self._type == 'delete':
            return
        if self._type in ('insert', 'replace'):
            return
        for src in self._sources:
            f_ = self._source_softdelete_filter(src)
            if f_ is None:
                continue
            self._add_where(f_)

    def _handle_foreign_attrs(self):
        if not self._columns:
            return
        for c in self._columns:
            if isinstance(c, AttributeAliased):
                c = c.c
            if not isinstance(c, ForeignAttr):
                continue
            c.validate()
            rel_obj_k = c.related_k
            rel_model_name = c.model.__name__
            rel_aj_name = "%s_%s" % (rel_model_name, rel_obj_k)
            if rel_aj_name not in self._autojoins:
                j_alias = self._get_free_table_alias('t')
                self._autojoins[rel_aj_name] = j_alias
                rel_c = getattr(c.model, rel_obj_k)
                rel_c.validate()
                j_src = rel_c.foreign_model.as_(j_alias)
                j_on_args = list()
                foreign_model = rel_c.foreign_model
                foreign_c = rel_c.foreign_c
                for x in xrange(len(foreign_c.columns)):
                    if foreign_c.model == c.model:
                        fc_ = getattr(foreign_model, foreign_c.ref_columns[x])
                        tfc_ = getattr(t_(j_alias, foreign_model), fc_.tbl_k)
                        lc_ = getattr(c.model, foreign_c.columns[x])
                    else:
                        fc_ = getattr(foreign_model, foreign_c.columns[x])
                        tfc_ = getattr(t_(j_alias, foreign_model), fc_.tbl_k)
                        lc_ = getattr(c.model, foreign_c.ref_columns[x])
                    j_on_args.append(tfc_ == lc_)
                self.left_join(j_src, *j_on_args)

    def _handle_related_attrs(self):
        if self._type != 'select':
            return
        resulting_model = self.resulting_model
        if issubclass(resulting_model, CompositeOrmModel):
            return
        if self.only_own:
            return
        attrs = resulting_model.__meta__.get_related_to_one_attributes()
        for c in attrs:
            if c.always_deferred:
                continue
            c.validate()
            j_alias = self._get_free_table_alias('t')
            j_src = c.foreign_model.as_(j_alias)
            j_on_args = list()
            foreign_model = c.foreign_model
            foreign_c = c.foreign_c
            self._related_objects[c.model_k] = (j_alias, foreign_model, list(), foreign_c)
            for x in xrange(len(foreign_c.columns)):
                if foreign_c.model == c.model:
                    fc_ = getattr(foreign_model, foreign_c.ref_columns[x])
                    tfc_ = getattr(t_(j_alias, foreign_model), fc_.tbl_k)
                    lc_ = getattr(c.model, foreign_c.columns[x])
                else:
                    fc_ = getattr(foreign_model, foreign_c.columns[x])
                    tfc_ = getattr(t_(j_alias, foreign_model), fc_.tbl_k)
                    lc_ = getattr(c.model, foreign_c.ref_columns[x])
                j_on_args.append(tfc_ == lc_)
            self.left_join(j_src, *j_on_args)

            attrs = foreign_model.__meta__.get_attributes_for_select()
            for fc in attrs:
                fc_alias = fc.tbl_k or fc.model_k
                fc_ = RequestTableBelongedColumn(fc_alias, j_alias, fc)
                self._add_attribute(fc_)
                self._related_obj_attrs.append(fc_)
                self._related_objects[c.model_k][2].append(fc_)

    def _finish(self, for_union=False):
        if self._is_finished:
            raise OrmRequestError(
                "Trying to modify request which is already finished and SQL query already prepared!"
            )
        self._is_finished = True
        if for_union:
            self._union = True
        self._name_unnamed_sources()
        self._handle_foreign_attrs()
        self._fillup_columns()
        self._handle_related_attrs()
        self._name_unnamed_columns()
        self._handle_softdelete_select()

    def _sql_delete(self):
        return self._sql_harddelete() \
            if self._sources[0].__meta__.soft_delete is None or self.hard_delete \
            else self._sql_softdelete()

    def _sql_softdelete(self):
        q_sources = self._sql_sources()
        q_where = self._sql_where()
        q_set = self._sql_softdelete_set()
        p = list()
        p.append("UPDATE")
        p.append(q_sources)
        p.append("SET")
        p.append(q_set)
        if q_where:
            p.append("WHERE")
            p.append(q_where)
        return " ".join(p)

    def _sql_harddelete(self):
        q_sources = self._sql_sources()
        q_where = self._sql_where()
        p = list()
        p.append("DELETE")
        # ps_ = list()
        # for src in self._sources:
        #     tbl_alias = src.alias if isinstance(src, OrmModelAliased) else self._models[src]
        #     ps_.append(tbl_alias)
        # p.append(",".join(ps_))
        p.append("FROM")
        p.append(q_sources)
        if q_where:
            p.append("WHERE")
            p.append(q_where)
        return " ".join(p)

    def _sql_write(self, cmd):
        q_sources = self._sql_sources()
        q_where = self._sql_where() if cmd not in ('insert', 'replace') else False
        q_columns = self._sql_columns() if cmd != 'insert' else self._sql_insert_columns()
        p = list()
        p.append(cmd.upper())
        if self.ignore:
            p.append('IGNORE')
        if cmd in ('insert', 'replace'):
            p.append('INTO')
        p.append(q_sources)
        if cmd == 'insert':
            p.append("(" + q_columns + ")")
            p.append("VALUES")
            p.append("(" + self._sql_insert_values() + ")")
        else:
            p.append("SET")
            p.append(q_columns)
            if q_where:
                p.append("WHERE")
                p.append(q_where)
        if not q_columns:
            return None
        return " ".join(p)

    def _sql_select(self, for_union=False, page=None, per_page=None, limit=None):
        if page is not None and not per_page:
            raise OrmRequestError(
                "When selecting only a page from an entire list - the parameter 'per_page' is required"
                " along with 'page'!"
            )
        if page and limit:
            raise OrmRequestError(
                "Parameters 'page' and 'limit' are mutual exclusive and cannot be specified both!"
            )
        q_sources = self._sql_sources()
        q_columns = self._sql_columns()
        q_where = self._sql_where()
        q_having = self._sql_having()
        if page is not None or limit is not None:
            if not self._union or self._union is True:
                q_limit = "" \
                    if limit is False \
                    else (self._sql_limit(limit)
                          if limit and isinstance(limit, RequestLimit)
                          else (self._sql_limit(RequestLimit(per_page * (page - 1), per_page)) if page else ""))
            else:
                q_limit = ""
        else:
            q_limit = self._sql_limit()
        q_orderby = self._sql_orderby()
        q_groupby = self._sql_groupby()
        p = list()
        p.append("SELECT")
        if self.distinct:
            p.append("DISTINCT")
        if self.high_priority and not for_union:
            p.append("HIGH_PRIORITY")
        if self.straight_join:
            p.append("STRAIGHT_JOIN")
        if self.sql_small_result:
            p.append("SQL_SMALL_RESULT")
        if self.sql_big_result:
            p.append("SQL_BIG_RESULT")
        if self.sql_buffer_result and not for_union:
            p.append("SQL_BUFFER_RESULT")
        if self.sql_cache and not for_union:
            p.append("SQL_CACHE")
        elif self.sql_no_cache and not for_union:
            p.append("SQL_NO_CACHE")
        if self.sql_calc_found_rows and not for_union:
            p.append("SQL_CALC_FOUND_ROWS")
        p.append(q_columns)
        p.append("FROM")
        p.append(q_sources)
        if q_where:
            p.append("WHERE")
            p.append(q_where)
        if q_groupby:
            p.append("GROUP BY")
            p.append(q_groupby)
        if q_having:
            p.append("HAVING")
            p.append(q_having)
        if q_orderby:
            p.append("ORDER BY")
            p.append(q_orderby)
        if q_limit:
            p.append("LIMIT")
            p.append(q_limit)
        if self.for_update and not for_union:
            p.append("FOR UPDATE")
        elif self.lock_in_share_mode and not for_union:
            p.append("LOCK IN SHARE MODE")
        if not q_columns:
            return None
        sql = " ".join(p)

        if self._union is not None and self._union is not True and isinstance(self._union, list):
            sql = "(" + sql + ")"
            p = list()
            p.append(sql)
            for union in self._union:
                p.append("UNION" if not union[1] else "UNION ALL")
                p.append("(" + union[0].union_request(self) + ")")
            q_union_groupby = self._sql_union_groupby()
            q_union_orderby = self._sql_union_orderby()
            if page is not None or limit is not None:
                q_union_limit = "" \
                    if limit is False \
                    else (self._sql_union_limit(limit)
                          if limit and isinstance(limit, RequestLimit)
                          else (self._sql_union_limit(RequestLimit(per_page * (page - 1), per_page)) if page else ""))
            else:
                q_union_limit = self._sql_union_limit()
            if q_union_groupby:
                p.append("GROUP BY")
                p.append(q_union_groupby)
            # if q_having:
            #     p.append("HAVING")
            #     p.append(q_having)
            if q_union_orderby:
                p.append("ORDER BY")
                p.append(q_union_orderby)
            if q_union_limit:
                p.append("LIMIT")
                p.append(q_union_limit)
            sql = " ".join(p)

        return sql

    def union_request(self, context):
        self.session = context.session
        if not self._is_finished:
            self._finish(for_union=True)
        union_sql = self._sql_select(for_union=True)
        for k in self.params:
            if k not in context.params:
                context.params[k] = self.params[k]
                continue
            pn = "pu%i_" % len(context.params)
            rpn_f = "%(" + k + ")s"
            rpn_t = "%(" + pn + ")s"
            context.params[pn] = self.params[k]
            union_sql = union_sql.replace(rpn_f, rpn_t)
        return union_sql

    def _sql(self, page=None, per_page=None, limit=None):
        if not self._is_finished:
            self._finish()
        if self._type == 'select':
            return self._sql_select(page=page, per_page=per_page, limit=limit)
        elif self._type in ('update', 'insert', 'replace'):
            return self._sql_write(self._type)
        elif self._type == 'delete':
            return self._sql_delete()
        return None

    def _require_session(self, session=None):
        from .session import OrmSessionAbstract
        session = session or self.session
        if not session:
            model_ = None
            for src in self._sources:
                ms_ = src.model.__meta__.session if isinstance(src, OrmModelAliased) else src.__meta__.session
                if ms_ is not None:
                    model_ = src.model if isinstance(src, OrmModelAliased) else src
                    break
            session = manager.get_session(session=session, model=model_)
        if not session:
            raise OrmRequestError("No database connection session is specified!")
        if not isinstance(session, OrmSessionAbstract):
            raise OrmRequestError("Database connection session ('session') must be a type of (OrmSessionAbstract)!")
        self.session = session
        return session

    @property
    def sql(self):
        return self._sql()

    def get(self, *args):
        """ This method offers an opportunity to set a set of sources (Models) and/or attributes to be loaded
        from the database. """
        if not args:
            raise OrmRequestError("'get' method of OrmRequest requires a set of sources and/or attributes!")
        sources = list()
        for arg in args:
            if isinstance(arg, (OrmModelMeta, OrmModelAbstract, OrmModelAliased)):
                sources.append(arg)
            elif isinstance(arg, (DataAttributeAbstract, DbFunctionAbstract)):
                self._resulting_model = CompositeOrmModel
                self._add_attribute(arg)
            elif isinstance(arg, (AttributeAliased, RequestTableBelongedColumn)):
                self._resulting_model = CompositeOrmModel
                self._add_attribute(arg)
        if sources:
            self._requesting_sources = sources
        return self

    @property
    def resulting_model(self):
        return self._resulting_model \
               or (self._req_srcs[0]
                   if (len(self._req_srcs) == 1 or len(self._requesting_sources) == 1)
                   and not self.textual_options and not self._union
                   else CompositeOrmModel)

    def go(self, session=None, page=None, per_page=None, limit=None):
        """ Executes the previously prepared request (this one). """
        session = self._require_session(session)
        self.session = session
        query = self._sql(page=page, per_page=per_page, limit=limit)
        params = self.params
        if self._type != 'select':
            session.execute(query, params)
            return
        rows = session.query(query, params).all() if query else []
        result = OrmResult()
        result.session = session
        result.request = self
        result.query = query
        result.params = params
        result.rows = rows
        result.page = page
        result.per_page = per_page
        columns2sources = dict()
        for c in self._columns:
            if isinstance(c, (ColumnAttributeAbstract, DbFunctionAbstract)):
                c_src = c.model
            elif isinstance(c, RequestTableBelongedColumn):
                c_src = self._tbl_aliases[c.tbl_name]
            else:
                c_src = None
            if c_src is not None and c_src in self._src_belongs_to:
                c_src = self._src_belongs_to[c_src]
            columns2sources[c] = c_src
        instance_cls = self.resulting_model
        sz_col = len(self._req_columns) - len(self._related_obj_attrs)
        for row in rows:
            kw = dict()
            for x in xrange(sz_col):
                c = self._req_columns[x]
                value = row[x]
                src = columns2sources[c]
                k = None
                if isinstance(c, AttributeAliased):
                    k = c.alias
                    c = c.c
                if isinstance(c, RequestTableBelongedColumn):
                    model = self._tbl_aliases[c.tbl_name]
                    model_ = model.model if isinstance(model, OrmModelAliased) else model
                    c_ = getattr(model_, c.k)
                else:
                    c_ = c
                k = k or getattr(c_, 'model_k', None)
                if not k:
                    k = self._attrs[c]
                elif instance_cls is CompositeOrmModel and src is not None:
                    if len(self._req_srcs) != 1 and len(self._requesting_sources) != 1:
                        model_name = src.alias if isinstance(src, OrmModelAliased) else src.__name__
                        k = "%s__%s" % (model_name, k)
                kw[k] = value, c_, src
            kw['__textual__'] = self.textual_options
            instance = self._create_loaded_instance(instance_cls, None, **kw)
            x = sz_col
            for rel_k in self._related_objects:
                finstance_cls = self._related_objects[rel_k][1]
                fattrs = self._related_objects[rel_k][2]
                relation_c = self._related_objects[rel_k][3]
                sz_fcol = len(fattrs)
                kw = dict()
                for n in xrange(sz_fcol):
                    c = self._req_columns[x]
                    value = row[x]
                    src = columns2sources[c]
                    k = c.k if isinstance(c, RequestTableBelongedColumn) else c.model_k
                    kw[k] = value, c, src
                    x += 1
                f_pk = finstance_cls.__meta__.get_primary_key()
                is_existing = False
                for cpk_ in f_pk:
                    kpk_ = cpk_.model_k
                    if kpk_ not in kw:
                        continue
                    vpk_ = kw[kpk_]
                    if vpk_[0] is not None:
                        is_existing = True
                        break
                if not is_existing:
                    continue
                kw['__textual__'] = self.textual_options
                related_instance = self._create_loaded_instance(finstance_cls, (instance, relation_c), **kw)
                rel_c = instance.__getattrabs__(rel_k)
                rel_c.set_value(instance, rel_k, related_instance)
            result.objects.append(instance)
        return result

    def _create_loaded_instance(self, __model__, __parent__=None, **kwargs):
        if isinstance(self.with_values, dict):
            for k in self.with_values:
                kwargs[k] = self.with_values[k]
        if isinstance(self.with_default, dict):
            for k in self.with_default:
                if k in kwargs:
                    continue
                kwargs[k] = self.with_default[k]
        instance = __model__()
        instance.__existing__ = True
        instance.__session__ = self.session
        instance.__parent__ = __parent__
        instance.__load__(**kwargs)
        return instance

    def count(self, session=None):
        if self._type != 'select':
            raise OrmRequestError("Method 'count()' can be called for selecting requests only!")
        session = self._require_session(session)
        q = "SELECT COUNT(1) FROM (" + self._sql(limit=False) + ") AS __tcount__"
        r = session.query(q, self.params).one()
        if not r:
            return None
        return int(r[0])

    def using(self, session):
        self.session = session

    def with_values(self, **kwargs):
        if self._type != 'select':
            raise OrmRequestError("'with_values' can be used with SELECT requests only!")
        if not isinstance(self.with_values, dict):
            self.with_values = dict()
        for k in kwargs:
            self.with_values[k] = kwargs[k]

    def with_default(self, **kwargs):
        if self._type != 'select':
            raise OrmRequestError("'with_default' can be used with SELECT requests only!")
        if not isinstance(self.with_default, dict):
            self.with_default = dict()
        for k in kwargs:
            self.with_default[k] = kwargs[k]

    def textual(self):
        self.textual_options = True
        return self

    def where(self, *expr):
        self._add_where(*expr)
        return self

    def having(self, *expr):
        self._add_having(*expr)
        return self

    def filter(self, *expr):
        return self.where(*expr)

    def join(self, model, *args):
        return self.left_join(model, *args)

    def left_join(self, model, *args):
        self._add_join(left_join_(model, *args))
        return self

    def right_join(self, model, *args):
        self._add_join(right_join_(model, *args))
        return self

    def inner_join(self, model, *args):
        self._add_join(inner_join_(model, *args))
        return self

    def full_join(self, model, *args):
        self._add_join(full_join_(model, *args))
        return self

    def union(self, *args):
        if self._type != 'select':
            raise OrmRequestError("cannot UNION when request is not SELECT!")
        for arg in args:
            if not isinstance(arg, OrmRequest):
                raise OrmRequestError("'union' method requires another OrmRequest to be given!")
            if self._union is None or self._union is True:
                self._union = list()
            self._union.append((arg, False))
        return self

    def union_all(self, *args):
        if self._type != 'select':
            raise OrmRequestError("cannot UNION ALL when request is not SELECT!")
        for arg in args:
            if not isinstance(arg, OrmRequest):
                raise OrmRequestError("'union_all' method requires another OrmRequest to be given!")
            if self._union is None or self._union is True:
                self._union = list()
            self._union.append((arg, True))
        return self

    def limit(self, *args):
        self._set_limit(RequestLimit(*args))
        return self

    def order_by(self, *args):
        if len(args) == 2 \
                and isinstance(args[1], str) \
                and args[1].upper() in ('ASC', 'DESC') \
                and isinstance(args[0], (ColumnAttributeAbstract, AttributeAliased, RequestTableBelongedColumn, str, int)):
            self._add_orderby(RequestOrderBy(args[0], args[1]))
            return self
        for arg in args:
            if isinstance(arg, (list, tuple)):
                if len(arg) != 2:
                    raise OrmRequestError(
                        "ORDER BY may be set using attributes or a (list|tuple) type array, first element of"
                        " which is an attribute and the second is a direction: ASC or DESC!"
                    )
                c = arg[0]
                d = arg[1]
                self._add_orderby(RequestOrderBy(c, d))
            else:
                self._add_orderby(RequestOrderBy(arg))
        return self

    def group_by(self, *args):
        if len(args) == 2 \
                and isinstance(args[1], str) \
                and args[1].upper() in 'ASC, DESC' \
                and isinstance(args[0], (ColumnAttributeAbstract, AttributeAliased, RequestTableBelongedColumn)):
            self._add_groupby(RequestGroupBy(args[0], args[1]))
            return self
        for arg in args:
            if isinstance(arg, (list, tuple)):
                if len(arg) != 2:
                    raise OrmRequestError(
                        "GROUP BY may be set using attributes or a (list|tuple) type array, first element of"
                        " which is an attribute and the second is a direction: ASC or DESC!"
                    )
                c = arg[0]
                d = arg[1]
                self._add_groupby(RequestGroupBy(c, d))
            else:
                self._add_groupby(RequestGroupBy(arg))
        return self

    @property
    def request_type(self):
        return self._type

    @property
    def first(self):
        if not self._limit:
            self.limit(1)
        return self.go().first

    @property
    def last(self):
        return self.go().last

    def one(self, x=None):
        if x is None:
            return self.first
        if not self._limit:
            self.limit(x, 1)
            return self.go().first
        return self.go().one(x)


class OrmSelectRequest(OrmRequest):
    def __init__(self, *args, **kwargs):
        super(OrmSelectRequest, self).__init__(REQUEST_SELECT, *args, **kwargs)


class OrmUpdateRequest(OrmRequest):
    def __init__(self, *args, **kwargs):
        super(OrmUpdateRequest, self).__init__(REQUEST_UPDATE, *args, **kwargs)


class OrmInsertRequest(OrmRequest):
    def __init__(self, *args, **kwargs):
        super(OrmInsertRequest, self).__init__(REQUEST_INSERT, *args, **kwargs)

    @property
    def inserted_id(self):
        if self._inserted_id:
            return self._inserted_id
        elif self.session.dbms_type == 'mysql':
            r = self.session.query("SELECT LAST_INSERT_ID()").one()
            if not r:
                raise Exception("Cannot retrieve LAST_INSERT_ID from DBMS")
            if not r[0]:
                raise Exception("Cannot retrieve LAST_INSERT_ID from DBMS, got %s" % str(r[0]))
            self._inserted_id = int(r[0])
            return int(r[0])
        elif self.session.dbms_type == 'postgresql':
            if self._sources[0].__meta__.auto_increment is None:
                raise OrmModelClassMismatch(
                    "OrmModel '%s' has no auto-increment key defined!" % self._sources[0].__class__.__name__
                )
            tbl_name = self._sources[0].table
            column_name = self._sources[0].__meta__.get_autoincrement().tbl_k
            q = "SELECT CURRVAL(pg_get_serial_sequence('%s', '%s'));" % (tbl_name, column_name)
            r = self.session.query(q).one()
            if not r:
                raise Exception("Cannot retrieve LAST_INSERT_ID from DBMS")
            if not r[0]:
                raise Exception("Cannot retrieve LAST_INSERT_ID from DBMS, got %s" % str(r[0]))
            self._inserted_id = int(r[0])
            return int(r[0])
        return None


class OrmReplaceRequest(OrmRequest):
    def __init__(self, *args, **kwargs):
        super(OrmReplaceRequest, self).__init__(REQUEST_REPLACE, *args, **kwargs)


class OrmDeleteRequest(OrmRequest):
    def __init__(self, *args, **kwargs):
        super(OrmDeleteRequest, self).__init__(REQUEST_DELETE, *args, **kwargs)


class OrmUndeleteRequest(OrmRequest):
    def __init__(self, *args, **kwargs):
        super(OrmUndeleteRequest, self).__init__(REQUEST_UNDELETE, *args, **kwargs)


class OrmSearchRequest(OrmRequest):
    def __init__(self, model, what, *args, **kwargs):
        super(OrmSearchRequest, self).__init__(REQUEST_SELECT, model, *args, **kwargs)
        if not isinstance(what, str):
            raise OrmParameterError("'find' method requires a search phrase of type of (str)!")
        findable_attrs = model.__meta__.get_findable_attributes()
        if not findable_attrs:
            raise OrmModelDeclarationError(
                "cannot 'find' over Model which there are no 'findable' attributes declared for it!"
            )
        phrases = split_search_phrase(what)
        w = list()
        for c in findable_attrs:
            if c.strict_find:
                w.append(c.in_(phrases))
            else:
                for phrase in phrases:
                    w.append(c.find_(phrase))
        self._add_where(or_(*w))


