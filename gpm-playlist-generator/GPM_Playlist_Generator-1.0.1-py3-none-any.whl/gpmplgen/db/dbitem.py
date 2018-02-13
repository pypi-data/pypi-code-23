import string


class DbItem:

    def __init__(self, columns):
        self._columns = columns

    def get_columns(self):
        names = map(lambda c: c.get_name(), self._columns)
        return ",".join(names)

    def get_schema_inner(self):
        definition = map(lambda c: c.get_column_def(), self._columns)
        return ",".join(definition)

    def get_schema(self):
        return '(' + self.get_schema_inner() + ')'

    def from_db_row(self, row):
        i = 0
        for c in self._columns:
            a = c.get_name()
            setattr(self, a, row[i])
            i += 1

    def sql_field_parameters(self):
        """Generate a parameterized string"""
        placeholder = []
        for _ in self._columns:
            placeholder.append('?')
        return '(' + ",".join(placeholder) + ')'

    def values(self):
        values = ()
        for c in self._columns:
            values = values + (getattr(self, c.get_name()),)
        return values


class DbColumn:
    def __init__(self, name, column_type):
        self.name = name
        self.type = column_type

    def get_name(self):
        return self.name

    def get_column_def(self):
        return '%s %s' % (self.name, self.type.upper())
