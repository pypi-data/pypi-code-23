class Expression(object):

    sql = None
    field = None
    alias = None


    def __init__(self, field, alias=None):
        self.field = field
        self.alias = alias


    def validate_as_field(self, sql):
        self.sql = sql
        sql.validate_field_name(self.field)


    def validate_as_filter(self, sql):
        self.sql = sql
        sql.validate_filter_field_name(self.field)


    def get_data(self):
        return []


    def __str__(self):
        return ''


    @property
    def data(self):
        return self.get_data()
