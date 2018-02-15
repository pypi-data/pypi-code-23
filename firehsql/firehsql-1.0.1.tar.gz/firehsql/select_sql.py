from .expressions import Expression
from .field import Field
from .filter_by import FilterByMixin
from .order_by import OrderByMixin
from .sql import SQL


class SelectSQL(SQL, FilterByMixin, OrderByMixin):

    vtable = None

    fields = None
    page_size = None
    page_offset = None
    groupby_exprs = None
    having_exprs = None
    distinct_field = None

    def __init__(self, schema, alias, vtable):
        super(SelectSQL, self).__init__(schema=schema, alias=alias)
        self.vtable = vtable
        self.fields = []
        self.groupby_exprs = []
        self.having_exprs = []


    def clear_fields(self):
        self.fields = []


    def set_distinct(self, field):
        if isinstance(field, str):
            field = self.field(field)

        self.validate_order_field_name(field)
        self.distinct_field = field
        self._order_fields = [o for o in self._order_fields\
                if str(o[0]) != str(field)]

        self._order_fields.insert(0, (field, False))


    def set_fields(self, *fields):
        for field in fields:
            if isinstance(field, Expression):
                field.validate_as_field(self)
            elif isinstance(field, Field):
                self.validate_select_field_name(field)
            elif isinstance(field, (list, tuple)):
                self.validate_select_field_name(field[0])
                field = self.field(field[0], field[1])
            else:
                self.validate_select_field_name(field)
                field = self.field(field)

            self.fields.append(field)


    def set_limit(self, size, offset=None):
        if size is None:
            self.page_size = None
        else:
            self.page_size = int(size)

        if offset is not None:
            self.page_offset = int(offset)


    def set_group_by(self, *expressions):
        for expression in expressions:
            if isinstance(expression, Field):
                self.validate_field_name(expression)
            elif isinstance(expression, str):
                self.validate_field_name(expression)
                expression = self.field(expression)
            elif isinstance(expression, Expression):
                expression.validate_as_field(self)
            else:
                raise RuntimeError('SelectSQL.set_group_by ' +\
                        'only supports field name or expression.')

            self.groupby_exprs.append(expression)


    def set_having(self, *expressions):
        for expression in expressions:
            if isinstance(expression, Expression):
                expression.validate_as_field(self)
            else:
                raise RuntimeError('SelectSQL.set_having ' +\
                        'only supports expression.')

            self.having_exprs.append(expression)


    def add_join(self, join_sql, join_type, *filters):
        self.relation[join_sql.name] = join_sql

        join_sql.set_host(self, join_type)
        join_sql.set_join_filters(*filters)


    def get_render_fields_data(self):
        for field in self.fields:
            if isinstance(field, Expression):
                for data in field.data:
                    yield data

        for key, relation in self.relation.items():
            if key != self.name:
                for data in relation.get_render_fields_data():
                    yield data


    def get_render_filters_data(self):
        for filter_ in self.filters:
            for data in filter_.data:
                yield data

        for key, relation in self.relation.items():
            if key != self.name:
                for data in relation.get_render_filters_data():
                    yield data


    def get_data(self):
        for data in self.get_render_fields_data():
            yield data

        if self.vtable:
            for data in self.vtable.data:
                yield data

        for key, relation in self.relation.items():
            if key != self.name:
                for data in relation.data:
                    yield data

        for data in self.get_render_filters_data():
            yield data

        for expression in self.groupby_exprs:
            if isinstance(expression, Expression):
                for data in expression.data:
                    yield data

        for expression in self.having_exprs:
            if isinstance(expression, Expression):
                for data in expression.data:
                    yield data


    def get_render_fields(self):
        for f in self.fields:
            yield str(f)

        for key, relation in self.relation.items():
            if key != self.name:
                for f in relation.get_render_fields():
                    yield f


    def get_render_filters(self):
        for f in self.filters:
            yield f

        for key, relation in self.relation.items():
            if key != self.name:
                for f in relation.get_render_filters():
                    yield f


    def render_fields(self):
        fields = list(self.get_render_fields())
        if fields:
            return ', '.join(str(f) for f in fields)
        return '*'


    def __str__(self):
        sql = ['SELECT']

        if self.distinct_field:
            sql.append('DISTINCT ON (%s)' % str(self.distinct_field))

        sql.append(self.render_fields())

        if self.vtable:
            sql.append('FROM (%s)' % str(self.vtable))
        else:
            sql.append('FROM ' + self.schema.TABLE_NAME)

        if self.alias:
            sql.append(self.alias)

        for key, relation in self.relation.items():
            if key != self.name:
                sql.append(str(relation))

        filters = list(self.get_render_filters())
        if filters:
            if len(filters) > 1:
                filter_ = self.create_and_filter(*filters)
            else:
                filter_ = filters[0]

            filter_ = str(filter_)
            if filter_:
                sql.append('WHERE ' + filter_)

        if self.groupby_exprs:
            sql.append('GROUP BY ' + ', '.join(str(expr) \
                    for expr in self.groupby_exprs))

        if self.having_exprs:
            sql.append('HAVING ' + ', '.join(str(expr) \
                    for expr in self.having_exprs))

        expression = ', '.join(self.order_fields)
        if expression:
            sql.append('ORDER BY ' + expression)

        if self.page_size and self.page_size > 0:
            sql.append('LIMIT %i OFFSET %i' % (self.page_size,
                    self.page_offset or 0))

        return ' '.join(sql)
