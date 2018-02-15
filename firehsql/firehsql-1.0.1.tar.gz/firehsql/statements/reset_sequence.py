from .statement import Statement


class ResetSequenceStatement(Statement):

    field = None

    def __init__(self, schema, field):
        super(ResetSequenceStatement, self).__init__(schema)
        self.field = field


    def __str__(self):
        data = {
            'table': self.schema.TABLE_NAME,
            'field': str(self.field),
        }
        return """SELECT setval(
            pg_get_serial_sequence('%(table)s', '%(field)s'),
            COALESCE((SELECT MAX(%(field)s) + 1 FROM %(table)s), 1),
            false)""" % data
