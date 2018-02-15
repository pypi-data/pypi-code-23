from .expressions import Expression
from .sql import SQL
from .statements import OnConflictUpdate


class InsertSQL(SQL):

    fields = None
    on_conflict = None

    def __init__(self, schema, alias):
        super(InsertSQL, self).__init__(schema=schema, alias=alias)
        self.fields = {}
        self.on_conflict = {}


    def set_values(self, **kwargs):
        for key, value in kwargs.items():
            self.validate_insert_field_name(key)
            if isinstance(value, Expression):
                value.validate_as_field(self.schema)

            self.fields[key] = value


    def create_on_conflict_statement(self):
        return OnConflictUpdate(schema=self.schema, alias=self.alias)


    def set_on_conflict(self, statement, *fields):
        # compatibility
        if isinstance(statement, OnConflictUpdate):
            # new behaviour
            for field in fields:
                self.validate_insert_field_name(field)

            trigger = ', '.join(sorted(str(f) for f in fields))
        else:
            # old behaviour
            self.validate_insert_field_name(statement)
            trigger = str(statement)
            statement = fields[0]

        if statement is None:
            self.on_conflict[trigger] = 'DO NOTHING'
        else:
            self.on_conflict[trigger] = statement


    def get_data(self):
        for value in self.fields.values():
            if isinstance(value, Expression):
                for expr_data in value.data:
                    yield expr_data
            else:
                yield value

        for statement in self.on_conflict.values():
            try:
                for data in statement.data:
                    yield data
            except AttributeError:
                pass


    def __str__(self):
        sql = [
            'INSERT INTO ' + self.schema.TABLE_NAME,
            '(%s)' % ', '.join(self.fields.keys()),
        ]

        values = []
        for value in self.fields.values():
            if isinstance(value, Expression):
                values.append(str(value))
            else:
                values.append(self.schema.PLACEHOLDER)
        sql.append('VALUES (%s)' % ', '.join(values))

        for trigger, statement in self.on_conflict.items():
            sql.append('ON CONFLICT (%s) %s' % (str(trigger), str(statement)))

        if self.schema.RETURNING_FIELDS:
            sql.append('RETURNING ' + ', '.join(self.schema.RETURNING_FIELDS))

        return ' '.join(sql)
