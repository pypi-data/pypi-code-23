from ..field import Field
from .expression import Expression

class Generic(Expression):
    """ Create free SQL expression.

    Example:

        sql = Schema.create_update_sql()
        sql.set_values(
            average=Generic(
                '({f} + {v}) / 2', # f == field and v == value
                                   # both are reserved words
                'average',         # the table's field to change
                123                # the value; can also be list, tuple or None
            ),
            total=Generic(
                '{f0} * {f1}',
                ['price', count'],
            ),
            price=Generic(
                '{f} - {v} - {v}',
                'price',
                [20, 10],
            ),
        )

    """
    fields = None
    expression = None
    values = None

    def __init__(self, expression, fields=None, values=None, alias=None):
        super(Generic, self).__init__(None)

        self.fields = fields
        self.alias = alias
        self.expression = expression
        self.values = values

        self.expression = self.expression.replace('{f}', '{f0}')

        if isinstance(values, str):
            self.values = [values]
        else:
            self.values = values


    def validate_as_field(self, sql):
        self.sql = sql

        if sql.schema.PLACEHOLDER in self.expression:
            raise ValueError('Invalid characters: ' + sql.schema.PLACEHOLDER +\
                    ' in expression: "' + self.expression + '"' +\
                    ' for table: ' + sql.schema.TABLE_NAME + '.')

        if isinstance(self.fields, (str, Field)):
            sql.validate_field_name(str(self.fields))

            self.fields = [self.fields]
        elif isinstance(self.fields, (list, tuple)):
            for field in self.fields:
                sql.validate_field_name(str(field))


    def validate_as_filter(self, sql):
        self.sql = sql

        if sql.schema.PLACEHOLDER in self.expression:
            raise ValueError('Invalid characters: ' + sql.schema.PLACEHOLDER +\
                    ' in expression: "' + self.expression + '"' +\
                    ' for table: ' + sql.schema.TABLE_NAME + '.')

        if isinstance(self.fields, (str, Field)):
            sql.validate_filter_field_name(str(self.fields))

            self.fields = [self.fields]
        elif isinstance(self.fields, (list, tuple)):
            for field in self.fields:
                sql.validate_filter_field_name(str(field))


    def get_data(self):
        if self.values:
            for value in self.values:
                yield value


    def __str__(self):
        replacement = {}

        if self.fields:
            for ii, field in enumerate(self.fields):
                replacement['f%i' % ii] = self.sql.altname(field)

        if self.values:
            replacement['v'] = self.schema.PLACEHOLDER

        if replacement:
            expr = self.expression.format(**replacement)
        else:
            expr = self.expression

        if self.alias:
            expr += ' AS ' + self.alias

        return expr
