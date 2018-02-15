from .delete_sql import DeleteSQL
from .insert_sql import InsertSQL
from .select_sql import SelectSQL
from .update_sql import UpdateSQL
from .join_sql import JoinSQL


class SchemaBase(object):

    TABLE_NAME = None

    FIELDS = ('id',)

    PRIMARY_KEY_FIELDS = ('id',)

    INSERT_FIELDS = () # Whitelist fields of Insert Query
    SELECT_FIELDS = () # Whitelist fields returned by Select Query
    UPDATE_FIELDS = () # Whitelist fields of Update Query

    FILTER_BY_FIELDS = () # Whitelist fields can be used in WHERE clause
    ORDER_BY_FIELDS = () # Whitelist fields can be used in ORDER BY clause

    DELETE_SQL_CLASS = DeleteSQL
    INSERT_SQL_CLASS = InsertSQL
    SELECT_SQL_CLASS = SelectSQL
    UPDATE_SQL_CLASS = UpdateSQL
    JOIN_SQL_CLASS = JoinSQL

    PLACEHOLDER = '%s' # used by psycopg2, and '?' for sqlite3
    RETURNING_FIELDS = () # fields in postgresql RETURNING clause


    @classmethod
    def literal_primary_key(cls):
        return ', '.join(cls.PRIMARY_KEY_FIELDS)


    @classmethod
    def create_delete_sql(cls, alias=None):
        return cls.DELETE_SQL_CLASS(cls, alias)


    @classmethod
    def create_insert_sql(cls, alias=None):
        return cls.INSERT_SQL_CLASS(cls, alias)


    @classmethod
    def create_select_sql(cls, alias=None, vtable=None):
        return cls.SELECT_SQL_CLASS(cls, alias, vtable)


    @classmethod
    def create_update_sql(cls, alias=None):
        return cls.UPDATE_SQL_CLASS(cls, alias)


    @classmethod
    def create_join_sql(cls, alias=None, vtable=None):
        return cls.JOIN_SQL_CLASS(cls, alias, vtable)


    @classmethod
    def validate_field_name(cls, name):
        is_valid = name in cls.FIELDS
        if not is_valid:
            raise ValueError('Invalid field: %s for table: %s.' % (
                    name, cls.TABLE_NAME))


    @classmethod
    def validate_insert_field_name(cls, name):
        is_valid = (cls.INSERT_FIELDS and name in cls.INSERT_FIELDS) or\
                (not cls.INSERT_FIELDS and name in cls.FIELDS)

        if not is_valid:
            raise ValueError('Invalid INSERT field: %s for table: %s.' % (
                    name, cls.TABLE_NAME))


    @classmethod
    def validate_select_field_name(cls, name):
        is_valid = (cls.SELECT_FIELDS and name in cls.SELECT_FIELDS) or\
                (not cls.SELECT_FIELDS and name in cls.FIELDS) or name == '*'

        if not is_valid:
            raise ValueError('Invalid SELECT field: %s for table: %s.' % (
                    name, cls.TABLE_NAME))


    @classmethod
    def validate_update_field_name(cls, name):
        is_valid = (cls.UPDATE_FIELDS and name in cls.UPDATE_FIELDS) or\
                (not cls.UPDATE_FIELDS and name in cls.FIELDS)

        if not is_valid:
            raise ValueError('Invalid UPDATE field: %s for table: %s.' % (
                    name, cls.TABLE_NAME))


    @classmethod
    def validate_filter_field_name(cls, name):
        is_valid = (cls.FILTER_BY_FIELDS and name in cls.FILTER_BY_FIELDS) or\
                (not cls.FILTER_BY_FIELDS and name in cls.FIELDS)

        if not is_valid:
            raise ValueError('Invalid WHERE field: %s for table: %s.' % (
                    name, cls.TABLE_NAME))


    @classmethod
    def validate_order_field_name(cls, name):
        is_valid = (cls.ORDER_BY_FIELDS and name in cls.ORDER_BY_FIELDS) or\
                (not cls.ORDER_BY_FIELDS and name in cls.FIELDS)

        if not is_valid:
            raise ValueError('Invalid ORDER BY field: %s for table: %s.' % (
                    name, cls.TABLE_NAME))
