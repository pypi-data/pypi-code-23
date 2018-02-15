from ..expressions import Expression
from ..update_sql import UpdateSQL

class OnConflictUpdate(UpdateSQL):

    def __str__(self):
        sql = ['DO UPDATE']

        expressions = []
        for key, value in self.fields.items():
            if isinstance(value, Expression):
                expressions.append('%s=%s' % (key, str(value)))
            else:
                expressions.append('%s=%s' % (key, self.schema.PLACEHOLDER))
        if expressions:
            sql.append('SET ' + ', '.join(expressions))

        if self.filters:
            if len(self.filters) > 1:
                filter_ = self.create_and_filter(*self.filters)
            else:
                filter_ = self.filters[0]

            filter_ = str(filter_)
            if filter_:
                sql.append('WHERE ' + filter_)

        return ' '.join(sql)
