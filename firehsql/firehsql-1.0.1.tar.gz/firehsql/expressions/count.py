from .expression import Expression

class Count(Expression):

    def validate_as_field(self, sql):
        self.sql = sql
        if self.field != '*':
            sql.schema.validate_field_name(str(self.field))


    def _get_field_name(self):
        if self.field == '*':
            return self.field

        return self.sql.absname(self.field)


    def __str__(self):
        assert self.sql is not None

        expr = 'COUNT(%s)' % self._get_field_name()

        if self.alias:
            expr += ' AS ' + self.alias

        return expr
