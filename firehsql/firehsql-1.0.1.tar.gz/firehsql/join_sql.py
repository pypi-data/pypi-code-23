from .select_sql import SelectSQL
from .filter_by import SQLFilter


class JoinSQL(SelectSQL):

    host = None
    join_type = None
    join_filters = None


    def __init__(self, schema, alias, vtable):
        super(JoinSQL, self).__init__(schema, alias, vtable)
        self.join_filters = []


    def set_host(self, sql, join_type):
        self.host = sql
        self.join_type = join_type


    def set_join_filters(self, *filters):
        flts = []
        for filter_ in filters:
            if isinstance(filter_, SQLFilter):
                self.join_filters.append(filter_)
            else:
                flts.append(filter_)

        if flts:
            self.join_filters.append(self.create_and_filter(*flts))


    def find_relation(self, name):
        # overrides one from SQL
        relation = super(JoinSQL, self).find_relation(name)
        if relation:
            return relation

        return self.host.find_relation(name)


    def get_has_join(self):
        # overrides one from SQL
        return len(self.relation) > 1 or len(self.host.relation) > 1


    def get_data(self):
        if self.vtable:
            for data in self.vtable.data:
                yield data

        for filter_ in self.join_filters:
            for data in filter_.data:
                yield data

        for key, relation in self.relation.items():
            if key != self.name:
                for data in relation.data:
                    yield data


    def __str__(self):
        sql = [self.join_type]

        if self.vtable:
            sql.append('(%s)' % str(self.vtable))
        else:
            sql.append(self.schema.TABLE_NAME)

        if self.alias:
            sql.append(self.alias)


        if len(self.join_filters) > 1:
            filter_ = self.create_and_filter(*self.join_filters)
        else:
            filter_ = self.join_filters[0]

        sql.append('ON ' + str(filter_))

        for key, relation in self.relation.items():
            if key != self.name:
                sql.append(str(relation))

        return ' '.join(sql)
