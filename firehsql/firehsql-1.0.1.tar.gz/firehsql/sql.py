from collections import OrderedDict
from .field import Field, split_field_name


class SQL(object):

    schema = None
    alias = None
    relation = None # connected SQL

    def __init__(self, schema, alias=None):
        super(SQL, self).__init__()
        self.schema = schema
        self.alias = alias
        self.relation = OrderedDict([(self.name, self)])


    @property
    def name(self):
        return self.alias or self.schema.TABLE_NAME


    def field(self, name, alias=None):
        return Field(self, name, alias)


    def find_relation(self, name):
        return self.relation.get(name)


    @property
    def data(self):
        return tuple(self.get_data())


    def get_data(self):
        raise NotImplementedError()


    @property
    def has_join(self):
        return self.get_has_join()


    def get_has_join(self):
        return len(self.relation) > 1


    def validate_field_name(self, field):
        table, name = split_field_name(field, self.name)
        relation = self.find_relation(table)
        if relation:
            relation.schema.validate_field_name(name)


    def validate_insert_field_name(self, field):
        table, name = split_field_name(field, self.name)
        relation = self.find_relation(table)
        if relation:
            relation.schema.validate_insert_field_name(name)


    def validate_select_field_name(self, field):
        table, name = split_field_name(field, self.name)
        relation = self.find_relation(table)
        if relation:
            relation.schema.validate_select_field_name(name)


    def validate_update_field_name(self, field):
        table, name = split_field_name(field, self.name)
        relation = self.find_relation(table)
        if relation:
            relation.schema.validate_update_field_name(name)


    def validate_filter_field_name(self, field):
        table, name = split_field_name(field, self.name)
        relation = self.find_relation(table)
        if relation:
            relation.schema.validate_filter_field_name(name)


    def validate_order_field_name(self, field):
        table, name = split_field_name(field, self.name)
        relation = self.find_relation(table)
        if relation:
            relation.schema.validate_order_field_name(name)
