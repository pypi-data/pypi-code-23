class Field(object):

    sql = None
    real_name = None
    alias = None

    def __init__(self, sql, name, alias=None):
        self.sql = sql
        self.real_name = name
        self.alias = alias


    @property
    def real_table(self):
        return self.sql.schema.TABLE_NAME


    @property
    def table(self):
        return self.sql.name


    @property
    def id(self):
        return self.sql.name + '.' + self.real_name


    def __str__(self):
        if self.sql.has_join:
            name = self.sql.name + '.' + self.real_name
        else:
            name = self.real_name

        if self.alias:
            name += ' AS ' + self.alias

        return name



def split_field_name(field, default_table=None):
    if isinstance(field, Field):
        return (field.table, field.real_name)
    else:
        # table_name.field_name
        try:
            table, name = field.split('.')
            return (table, name)
        except ValueError:
            # just field_name
            return (default_table, field)
