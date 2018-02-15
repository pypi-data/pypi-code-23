from .expression import Expression

class Average(Expression):

    def __str__(self):
        expr = 'AVG(%s)' % self.sql.absname(self.field)

        if self.alias:
            expr += ' AS ' + self.alias

        return expr
