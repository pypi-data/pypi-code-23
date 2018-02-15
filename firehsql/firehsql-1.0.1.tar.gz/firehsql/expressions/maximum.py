from .expression import Expression

class Maximum(Expression):

    def __str__(self):
        expr = 'MAX(%s)' % self.sql.absname(self.field)

        if self.alias:
            expr += ' AS ' + self.alias

        return expr
