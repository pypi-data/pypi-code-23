from .expression import Expression

class Sum(Expression):

    def __str__(self):
        expr = 'SUM(%s)' % self.sql.absname(self.field)

        if self.alias:
            expr += ' AS ' + self.alias

        return expr
