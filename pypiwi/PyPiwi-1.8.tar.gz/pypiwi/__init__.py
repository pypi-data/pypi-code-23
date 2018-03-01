# -*- coding: utf-8 -*-
import sys
import threading
from collections import OrderedDict
from contextlib import contextmanager

import peewee as p
import playhouse.migrate as m
import playhouse.signals as ps
from inflection import underscore
from peewee import BareField, BigIntegerField, BlobField, BooleanField, \
    CharField, Check, Clause, CompositeKey, DQ, DataError, DatabaseError, \
    DateField, DateTimeField, DecimalField, DeferredRelation, DoesNotExist, \
    DoubleField, Field, FixedCharField, FloatField, ForeignKeyField, \
    ImproperlyConfigured, IntegerField, IntegrityError, InterfaceError, \
    InternalError, JOIN, JOIN_FULL, JOIN_INNER, JOIN_LEFT_OUTER, MySQLDatabase, \
    NotSupportedError, OperationalError, Param, PostgresqlDatabase, \
    PrimaryKeyField, ProgrammingError, Proxy, R, SQL, SmallIntegerField, \
    SqliteDatabase, TextField, TimeField, TimestampField, UUIDField, Using, \
    Window, fn, prefetch
from playhouse.reflection import Introspector, UnknownField
from playhouse.shortcuts import dict_to_model, model_to_dict

peewee = (BareField, BigIntegerField, BlobField,
          BooleanField, CharField, Check, Clause, CompositeKey,
          DatabaseError, DataError, DateField, DateTimeField, DecimalField,
          DeferredRelation, DoesNotExist, DoubleField, DQ, Field,
          FixedCharField, FloatField, fn, ForeignKeyField,
          ImproperlyConfigured, IntegerField, IntegrityError,
          InterfaceError, InternalError, JOIN, JOIN_FULL, JOIN_INNER,
          JOIN_LEFT_OUTER, MySQLDatabase, NotSupportedError,
          OperationalError, Param, PostgresqlDatabase, prefetch,
          PrimaryKeyField, ProgrammingError, Proxy, R, SmallIntegerField,
          SqliteDatabase, SQL, TextField, TimeField, TimestampField, Using,
          UUIDField, Window)

try:
    import playhouse.postgres_ext as ppe
except ImportError:
    ppe = None
else:
    from playhouse.postgres_ext import (cast, ArrayField, DateTimeTZField,
                                        HStoreField, JSONField, BinaryJSONField,
                                        TSVectorField, Match,
                                        PostgresqlExtDatabase,
                                        ServerSideSelectQuery, ServerSide,
                                        LateralJoin)

    peewee += (cast, ArrayField, DateTimeTZField, HStoreField, JSONField,
               BinaryJSONField, TSVectorField, Match, PostgresqlExtDatabase,
               ServerSideSelectQuery, ServerSide, LateralJoin)

for item in peewee:
    assert item

AVG = p.fn.AVG
COUNT = p.fn.COUNT
MAX = p.fn.MAX
MIN = p.fn.MIN
SIMILARITY = p.fn.SIMILARITY
SUM = p.fn.SUM

db_table_name = underscore

db_lock = threading.Lock()


class Manager(object):
    """Manager allows for easy transactions and analyzing.
        
        manager = pp.Manager()
        
        class Model(pp.Model):
            class Meta(object):
                database = manager.proxy()
        
        class Person(Model):
            first = pp.CharField()
            
        analyser = manager.analyze()
        analyser.scan()
        analyser.auto_migrate()
        
        with manager.using():
            person = Person()
            person.first = 'John'
            person.save()
        
    """

    def __init__(self, database_class, database_name, **options):
        self.database_class = database_class
        self.database_name = database_name

        self.options = options
        self.models = list()

    @contextmanager
    def using(self):
        with p.Using(self.connection(), self.models) as using:
            yield using

    def connection(self):
        return self.database_class(database=self.database_name,
                                   **self.options)

    def proxy(self):
        return DatabaseProxy(self)

    def analyse(self):
        return Analyser(self, self.connection())


class ManagerPool(Manager):
    """Use the manager to manage connections to different databases.

    The class provides a `proxy` that can be used in your models. When calling
    `with using` on the manager, all models are automaticly switched to
    the given database. This allows for a _multple database_-style application
    where different customers have different databases, but share the schema.

    This is also very handy for switching between _testing_ and _production_
    databases without lots of configuration.
    """

    def __init__(self, database_class, database_name=None, **options):
        super(ManagerPool, self).__init__(database_class, database_name, **options)

        self.pool = dict()

    @contextmanager
    def using(self, database_name):
        with db_lock:
            connection = self.connection(database_name or self.database_name)
            with p.Using(connection, self.models) as using:
                yield using

    def connection(self, database_name):
        database_name = database_name or self.database_name
        if database_name not in self.pool:
            self.pool[database_name] = self.database_class(
                    database=database_name, **self.options)
        return self.pool[database_name]

    def proxy(self):
        return DatabaseProxy(self)

    def analyse(self, database):
        return Analyser(self, database)


class DatabaseProxy(p.Proxy):
    """
    Proxy class useful for situations when you wish to defer the initialization
    of an object.
    """
    __slots__ = ['obj', '_callbacks', 'manager']

    def __init__(self, manager):
        super(DatabaseProxy, self).__init__()
        self.manager = manager

    def initialize(self, obj):
        if obj is not None:
            raise RuntimeError('Please use `manager.using(database)`.')
        super(DatabaseProxy, self).initialize(obj)

    def register(self, model):
        self.manager.models.append(model)


class BaseModel(p.BaseModel):
    def __new__(cls, name, bases, attrs):
        cls = super(BaseModel, cls).__new__(cls, name, bases, attrs)
        if not hasattr(cls, '_meta'):
            return cls

        # overwrite db_table name with our underscore variant
        cls._meta.db_table = db_table_name(name)

        if len(cls._meta.fields.values()) > 1 and \
                isinstance(cls._meta.database, DatabaseProxy):
            cls._meta.database.register(cls)

        return cls


class Model(p.with_metaclass(BaseModel, p.Model), p.Model):
    def __init__(self, *args, **kwargs):
        super(Model, self).__init__(*args, **kwargs)
        ps.pre_init.send(self)

    def prepared(self):
        result = super(Model, self).prepared()
        ps.post_init.send(self)

        return result

    def save(self, force_insert=False, only=None, skip_triggers=False):
        pk_value = self._get_pk_value()
        created = force_insert or not bool(pk_value)

        if not skip_triggers:
            ps.pre_save.send(self, created=created)

        result = super(Model, self).save(force_insert=force_insert,
                                         only=only)

        if not skip_triggers:
            ps.post_save.send(self, created=created, result=result)

        return result

    def delete_instance(self, recursive=False, delete_nullable=False,
                        skip_triggers=False):
        if not skip_triggers:
            ps.pre_delete.send(self)

        result = super(Model, self).delete_instance(
                recursive=recursive, delete_nullable=delete_nullable)

        if not skip_triggers:
            ps.post_delete.send(self, result=result)

        return result

    @classmethod
    def get_or_none(cls, *args):
        """Get a resource, return None if it's not found.

        **Parameters**

        :param \*args: List of query expressions.
        :rtype: Model or None
        """
        try:
            return super(Model, cls).get(*args)
        except p.DoesNotExist:
            return None

    @classmethod
    def from_dict(cls, data, ignore_unknown=True):
        """Convert a dict to a model.

        **Parameters**

        :param data: A dictionary of data.
        :param ignore_unknown: Ignore unkown fields.
        :type data: dict
        :type ignore_unknown: bool
        :rtype: Model

        """
        return dict_to_model(cls, data, ignore_unknown)

    def to_dict(self, recurse=False, backrefs=False, only=None,
                exclude=None, seen=None):
        """
        Convert a model instance (and any related objects) to a dictionary.

        **Parameters**

        :param recurse: Whether foreign-keys should be recursed.
            Defaults to `False`.
        :param backrefs: Whether lists of related objects should be
            recursed.
            Defaults to `False`.
        :param only: A list (or set) of field instances indicating which
            fields should be included.
            Defaults to `None`.
        :param exclude: A list (or set) of field instances that should be
            excluded from the dictionary.
            Defaults to `None`.
        :param seen: Internally used.
            Defaults to `None`.
        :type recurse: bool
        :type backrefs: bool
        :type only: list
        :type exclude: list
        """
        return model_to_dict(self, recurse, backrefs, only, exclude, seen)

    def update_with(self, data, exclude=None):
        """Update the model with a dictionary.

        **Parameters**

        :param data: A dictionary of data, fields unknown are skipped.
        :param exclude: A list of keys that are to be excluded.
        :type data: dict
        :type exclude: list
        :rtype: Model

        """
        for key, value in data.items():
            if exclude and key in exclude:
                continue

            setattr(self, key, value)
        return self

    def save_dirty(self):
        """Only save the fields that are *dirty*."""
        return self.save(only=self.dirty_fields)

    @classmethod
    def meta_database(cls):
        """Retrieve the active database from the model."""
        return cls._meta.database

    @classmethod
    def meta_name(cls):
        """Retrieve the database table name of the model.

        :rtype: str
        """
        return cls._meta.db_table

    @classmethod
    def meta_fields(cls):
        """Retrieve all the fields of the model.

        :rtype: dict
        """
        return get_sorted_fields(cls)

    @classmethod
    def meta_field(cls, name):
        """Retrieve a field by name.

        :rtype: peewee.Field
        """
        return cls._meta.fields.get(name)


class Analyser(object):
    def __init__(self, manager, connection):
        self.manager = manager
        self.statements = list()

        self.connection = connection

        self.local = None
        self.online = None

        self.order_of_models = list()
        self.local_models = dict()
        self.online_models = dict()

    def scan(self):
        self.statements = list()

        models = p.sort_models_topologically(self.manager.models)
        self.order_of_models = [m._meta.db_table for m in models]
        self.local_models = {m._meta.db_table: m for m in models}

        with self.connection.atomic():
            self.local = Topology(self.connection, self.local_models)

            introspector = Introspector.from_database(self.connection)
            self.online_models = generate_models(introspector)
            self.online = Topology(self.connection, self.online_models)

        # first missing tables to be created
        for db_table in self.order_of_models:
            if db_table not in self.online.models:
                local_model = self.local.models[db_table]
                local_instance = local_model['instance']

                self.state('create_table', local_instance)

        # second all fields of the missing tables (fixes race conditions)
        for db_table in self.order_of_models:
            if db_table not in self.online.models:
                local_model = self.local.models[db_table]
                local_instance = local_model['instance']
                local_fields = local_model['fields']
                local_indexes = local_model['indexes']

                # fields to be added
                for field_name, local_field in local_fields.items():
                    if isinstance(local_field.field, PrimaryKeyField):
                        continue
                    self.state('add_column', local_instance, local_field, True)

                # scan indexes to be created
                for local_index in local_indexes:
                    self.state('add_index', local_instance, local_index)

        # third missing tables to be dropped
        for db_table, online_model in self.online.models.items():
            if db_table not in self.local.models:
                self.state('drop_table', online_model['instance'])

        # fourth scan fields to be created, dropped or mutate
        for db_table, online_model in self.online.models.items():
            if db_table not in self.local.models:
                continue

            local_model = self.local.models[db_table]

            online_instance = online_model['instance']
            local_instance = local_model['instance']

            online_fields = online_model['fields']
            local_fields = local_model['fields']

            online_indexes = online_model['indexes']
            local_indexes = local_model['indexes']

            # scan indexes to be dropped
            for online_index in online_indexes:
                found = any(l == online_index for l in local_indexes)
                if not found:
                    self.state('drop_index', online_instance, online_index)

            # fields to be dropped
            for field_name, online_field in online_fields.items():
                if field_name not in local_fields:
                    self.state('drop_column', local_instance, online_field)

            # fields to be added
            for field_name, local_field in local_fields.items():
                if field_name not in online_fields:
                    self.state('add_column', local_instance, local_field, False)

            # fields to be mutated
            for field_name, local_field in local_fields.items():
                if field_name not in online_fields:
                    continue

                online_field = online_fields[field_name]

                if local_field == online_field:
                    continue

                if local_field.test_modifiers_changed(online_field):
                    pass
                    # peewee currently does not support reflection based on
                    # the modifier, when changed it always triggers this
                    # "changed" element.
                elif local_field.test_null_changed(online_field):
                    if online_field.field.null:
                        self.state('add_not_null', local_instance, local_field)
                    else:
                        self.state('drop_not_null', local_instance,
                                   local_field)
                else:
                    skip = False

                    if local_field.sql != online_field.sql:
                        try:
                            from playhouse.postgres_ext import ArrayField
                            if isinstance(local_field, ArrayField):
                                skip = True
                        except ImportError:
                            pass

                    if skip:
                        self.state('drop_column', online_instance,
                                   online_field)
                        self.state('add_column', local_instance,
                                   local_field, False)

            # scan indexes to be created
            for local_index in local_indexes:
                found = any(l == local_index for l in online_indexes)
                if not found:
                    self.state('add_index', local_instance, local_index)

    def state(self, name, model, item=None, *args):
        self.statements.append([name, model, item] + list(args))

    @property
    def migrator(self):  # pragma: no cover
        if isinstance(self.connection, p.PostgresqlDatabase):
            return MigratorWrapper(PostgresqlMigrator(self.connection))
        elif isinstance(self.connection, p.MySQLDatabase):
            return MigratorWrapper(MySQLMigrator(self.connection))
        elif isinstance(self.connection, p.SqliteDatabase):
            return MigratorWrapper(SqliteMigrator(self.connection))
        else:
            raise RuntimeError('Unknown database type, cannot find migrator.')

    def auto_migrate(self, show_progress=True, out=None):
        if out is None:  # pragma: no cover
            from sys import stdout
            out = stdout

        if not len(self.statements):
            return False

        with self.connection.atomic():
            migrator = self.migrator

            total = len(self.statements)
            if show_progress:
                out.write('Running %d statements.\n' % total)
                out.flush()
            for sx, statement in enumerate(self.statements):
                if show_progress:
                    out.write('[%d/%d] %s\n' % (sx + 1, total, statement))
                    out.flush()
                migrator.run(statement)

        return True

    def print_migrations(self, out=None):
        if out is None:  # pragma: no cover
            from sys import stdout
            out = stdout

        write = out.write

        tpl = '{table:s} = DroppableTable("{table:s}")\n'
        drop_tables = [r for r in self.statements if r[0] == 'drop_table']

        if len(drop_tables):
            for name, table, item in drop_tables:
                write(tpl.format(table=table._meta.db_table))
            write('\n')

        for statement in self.statements:
            name = statement[0]
            table = statement[1]
            item = statement[2]

            db_table = table._meta.db_table

            write('migrator.{name:s}('.format(name=name))

            if name == 'create_table':
                write('m.' + table.__name__)
            elif name == 'drop_table':
                write(db_table)
            elif name == 'drop_column':
                write('m.' + table.__name__ + ', ')
                write('p.Field(db_column="' + item.field.db_column + '")')
            elif name == 'add_column':
                write('m.' + table.__name__ + ', ')
                write('m.' + table.__name__ + '.' + item.field.name)
            elif name == 'drop_not_null':
                write('m.' + table.__name__ + ', ')
                write('m.' + table.__name__ + '.' + item.field.name)
            elif name == 'add_not_null':
                write('m.' + table.__name__ + ', ')
                write('m.' + table.__name__ + '.' + item.field.name)
            elif name == 'add_index':
                write('m.' + table.__name__ + ', ')
                write('[')
                for field_name in item.field_names:
                    write('"' + field_name + '", ')
                write('], ')
                write('True' if item.unique else 'False')
            elif name == 'drop_index':
                write('m.' + table.__name__ + ', ')
                write('[')
                for field_name in item.field_names:
                    write('"' + field_name + '", ')
                write(']')
            else:  # pragma: no cover
                raise ValueError('Unknown migrator.')

            write(')\n')


def generate_models(introspector, skip_invalid=False, table_names=None,
                    literal_column_names=False):
    database = introspector.introspect(table_names=table_names,
                                       literal_column_names=literal_column_names)
    models = {}

    class BaseModel(Model):
        class Meta:
            database = introspector.metadata.database

    def _create_model(table, models):
        for foreign_key in database.foreign_keys[table]:
            dest = foreign_key.dest_table

            if dest not in models and dest != table:
                # this fixes the circulair referencing bug...
                models[table] = type(str(table), (BaseModel,), {})
                _create_model(dest, models)

        primary_keys = []
        columns = database.columns[table]
        for db_column, column in columns.items():
            if column.primary_key:
                primary_keys.append(column.name)

        multi_column_indexes = database.multi_column_indexes(table)
        column_indexes = database.column_indexes(table)

        class Meta:
            indexes = multi_column_indexes

        # Fix models with multi-column primary keys.
        composite_key = False
        if len(primary_keys) == 0:
            primary_keys = columns.keys()
        if len(primary_keys) > 1:
            Meta.primary_key = CompositeKey(*[
                field.name for col, field in columns.items()
                if col in primary_keys])
            composite_key = True

        attrs = {'Meta': Meta}
        for db_column, column in columns.items():
            FieldClass = column.field_class
            if FieldClass is UnknownField:
                FieldClass = BareField

            params = {
                'db_column': db_column,
                'null': column.nullable}
            if column.primary_key and composite_key:
                if FieldClass is PrimaryKeyField:
                    FieldClass = IntegerField
                params['primary_key'] = False
            elif column.primary_key and FieldClass is not PrimaryKeyField:
                params['primary_key'] = True
            if column.is_foreign_key():
                if column.is_self_referential_fk():
                    params['rel_model'] = 'self'
                else:
                    dest_table = column.foreign_key.dest_table
                    params['rel_model'] = models[dest_table]
                if column.to_field:
                    params['to_field'] = column.to_field

                # Generate a unique related name.
                params['related_name'] = '%s_%s_rel' % (table, db_column)
            if db_column in column_indexes and not column.is_primary_key():
                if column_indexes[db_column]:
                    params['unique'] = True
                elif not column.is_foreign_key():
                    params['index'] = True

            attrs[column.name] = FieldClass(**params)

        try:
            models[table] = type(str(table), (BaseModel,), attrs)
        except ValueError:
            if not skip_invalid:
                raise

    # Actually generate Model classes.
    for table, model in sorted(database.model_names.items()):
        if table not in models:
            _create_model(table, models)

    return models


class MigratorWrapper(object):
    def __init__(self, migrator):
        self.migrator = migrator

    def run(self, statement):
        name = statement[0]
        table = statement[1]
        item = statement[2]

        func = getattr(self, name)
        try:
            if name.endswith('_table'):
                func(table)
            elif name == 'add_column':
                func(table, item.field, statement[3])
            elif name == 'add_index':
                func(table, item.field_names, item.unique)
            elif name == 'drop_index':
                func(table, item.field_names)
            else:
                func(table, item.field)
        except Exception as exc:
            msg = 'Error on `{:s}` with `{:s}`.`{:s}`.'.format(
                    name, table._meta.db_table, str(item))

            msg += '\nOriginalError: ' + str(exc)
            msg += '\nStatement: ' + repr(statement)

            exc_type = type(exc)
            tb = sys.exc_info()[2]

            raise exc_type(msg).with_traceback(tb)

    def create_table(self, table):
        qc = self.migrator.database.compiler()  # type: p.QueryCompiler

        statement = 'CREATE TABLE'
        meta = table._meta

        columns, constraints = [], []
        if meta.composite_key:
            pk_cols = [meta.fields[f].as_entity()
                       for f in meta.primary_key.field_names]
            constraints.append(Clause(
                    SQL('PRIMARY KEY'), p.EnclosedClause(*pk_cols)))
        for field in meta.declared_fields:
            if isinstance(field, p.PrimaryKeyField):
                columns.append(qc.field_definition(field))

        sql, params = qc.parse_node(Clause(
                SQL(statement),
                table.as_entity(),
                p.EnclosedClause(*(columns + constraints))))

        self.migrator.database.execute_sql(sql, params)

    def drop_table(self, table):
        cascade = not isinstance(self.migrator, m.SqliteMigrator)
        self.migrator.database.drop_table(table, fail_silently=False,
                                          cascade=cascade)

    def drop_column(self, table, field):
        cascade = not isinstance(self.migrator, m.SqliteMigrator)
        self.migrator.drop_column(
                table._meta.db_table, field.db_column, cascade=cascade).run()

    def add_column(self, table, field, suppress):
        self.migrator.add_column(
                table._meta.db_table, field.db_column, field, suppress).run()

    def drop_not_null(self, table, field):
        self.migrator.drop_not_null(
                table._meta.db_table, field.db_column).run()

    def add_not_null(self, table, field):
        self.migrator.add_not_null(
                table._meta.db_table, field.db_column).run()

    def drop_index(self, table, fields):
        index_name = get_index_name(table, fields)

        self.migrator.drop_index(
                table._meta.db_table, index_name).run()

    def add_index(self, table, fields, unique):
        self.migrator.add_index(
                table._meta.db_table, fields, unique=unique).run()


def _override_add_column(me, table, column_name, field, suppress=False):
    # Adding a column is complicated by the fact that if there are rows
    # present and the field is non-null, then we need to first add the
    # column as a nullable field, then set the value, then add a not null
    # constraint.
    # EXTRA: Migrator is allowed to suppress the error.
    if not field.null and field.default is None and not suppress:
        raise ValueError('XXX %s is not null but has no default' % column_name)

    is_foreign_key = isinstance(field, ForeignKeyField)

    # Foreign key fields must explicitly specify a `to_field`.
    if is_foreign_key and not field.to_field:
        raise ValueError('Foreign keys must specify a `to_field`.')

    operations = [me.alter_add_column(table, column_name, field)]

    # In the event the field is *not* nullable, update with the default
    # value and set not null.
    if not field.null:
        operations.extend([
            me.apply_default(table, column_name, field),
            me.add_not_null(table, column_name)])

    if is_foreign_key and me.explicit_create_foreign_key:
        operations.append(
                me.add_foreign_key_constraint(
                        table,
                        column_name,
                        field.rel_model._meta.db_table,
                        field.to_field.db_column))

    return operations


class PostgresqlMigrator(m.PostgresqlMigrator):
    @m.operation
    def add_column(self, table, column_name, field, suppress=False):
        return _override_add_column(self, table, column_name, field, suppress)


class MySQLMigrator(m.MySQLMigrator):
    @m.operation
    def add_column(self, table, column_name, field, suppress=False):
        return _override_add_column(self, table, column_name, field, suppress)


class SqliteMigrator(m.SqliteMigrator):
    @m.operation
    def add_column(self, table, column_name, field, suppress=False):
        return _override_add_column(self, table, column_name, field, suppress)


class Topology(object):
    def __init__(self, connection, models):
        compiler = connection.compiler()

        self.models = dict()
        for db_table, model in models.items():
            self.models[db_table] = {
                'instance': model,
                'fields': OrderedDict(),
                'indexes': list(),
            }

            fields = self.models[db_table]['fields']
            indexes = self.models[db_table]['indexes']

            for n, f in get_sorted_fields(model).items():
                fields[n] = ComparableField(compiler, f)

            for index_field in model._fields_to_index():
                indexes.append(ComparableIndex(
                        [index_field], index_field.unique))

            for index_fields, unique in model._meta.indexes:
                try:
                    indexes.append(ComparableIndex(
                            [model._meta.fields[n] for n in index_fields], unique))
                except Exception as exc:
                    raise Exception(
                            'Cannot compare index %s -> %s.\n%s: %s' % (
                                db_table, str(index_fields),
                                exc.__class__.__name__, str(exc)))


class ComparableField(object):
    def __init__(self, compiler, field):
        """
        :type field: peewee.Field
        """
        self.compiler = compiler
        self.field = field
        self.db_name = field.db_column

        self.sql, self.params = self.get_definition()

    def __eq__(self, other):
        return repr(self) == repr(other)

    def __str__(self):
        return self.db_name

    def __repr__(self):
        return '<{:s} ({:s} [{:s}])>'.format(
                self.db_name, self.sql,
                ', '.join(str(v) for v in self.params))

    def get_definition(self, field=None):
        if field is None:
            field = self.field

        return self.compiler.parse_node(self.compiler.field_definition(field))

    def test_null_changed(self, other):
        clone = self.field.clone_base()

        if hasattr(clone, 'max_length') and hasattr(other.field, 'max_length'):
            clone.max_length = other.field.max_length

        clone.null = not clone.null

        return self.get_definition(clone) == other.get_definition()

    def test_modifiers_changed(self, other):
        clone = self.field.clone_base()

        clone_modifiers = '-'.join(str(m) for m
                                   in clone.get_modifiers() or list())
        other_modifiers = '-'.join(str(m) for m
                                   in other.field.get_modifiers() or list())

        if clone_modifiers == other_modifiers:
            return False

        for attr in ['max_length', 'max_digits', 'decimal_places']:
            setattr(clone, attr, getattr(other.field, attr, None))

        return self.get_definition(clone) == other.get_definition()


class ComparableIndex(object):
    def __init__(self, fields, unique):
        self.fields = fields
        self.field_names = [f.db_column for f in fields]
        self.unique = unique

    def __str__(self):
        return get_index_name(self.fields[0].model_class, self.field_names)

    def __eq__(self, other):
        return repr(self) == repr(other)

    def __repr__(self):
        # TODO: Report bug in sorted index names - peewee.py @3765
        if self.unique:
            return '<{:s} UNIQUE>'.format(', '.join(
                    sorted(self.field_names)))
        else:
            return '<{:s}>'.format(', '.join(
                    sorted(self.field_names)))


def get_sorted_fields(model):
    fields = OrderedDict()

    for n in model._meta.sorted_field_names:
        f = model._meta.fields[n]
        fields[n] = f

    return fields


def get_index_name(table, fields):
    # TODO: name of index may be incomplete
    return (table._meta.db_table + '_' + '_'.join(fields))[0:63]


class DroppableTable(object):
    def __init__(self, name):
        self.name = name

    def as_entity(self):
        return p.Entity(self.name)


# region Distill


def distill(cursor, fields):
    if fields is None:
        return cursor
    else:
        return [solve_record(x, fields) for x in cursor]


def solve_record(row, fields):
    """Solve a model into a dict using specified fields.

    :param Model row:
    :param List[str] fields:
    :rtype: dict
    """
    data = dict()
    recurse = dict()

    for field in fields:  # type: str
        if field == '*':
            data.update(row.to_dict())
        elif field.count('.') > 0:
            first, names = field.split('.', 1)
            recurse.setdefault(first, list())
            recurse[first].append(names)
        else:
            data[field] = getattr(row, field)

    for field, subfields in recurse.items():
        if subfields == ['*']:
            data[field] = getattr(row, field, None)
        else:
            value = getattr(row, field, None)

            if value is None:
                data[field] = None
            elif isinstance(value, p.SelectQuery):
                data[field] = distill(value, subfields)
            else:
                data[field] = solve_record(value, subfields)

    return data

# endregion
