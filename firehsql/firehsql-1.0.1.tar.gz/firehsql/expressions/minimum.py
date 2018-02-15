from .expression import Expression

class Minimum(Expression):

    def __str__(self):
        expr = 'MIN(%s)' % self.sql.absname(self.field)

        if self.alias:
            expr += ' AS ' + self.alias

        return expr
