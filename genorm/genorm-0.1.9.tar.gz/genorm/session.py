import inspect
from pc23 import xrange
from .mapper import mapper
from .exceptions import OrmException, OrmParameterError, OrmModelDeclarationError
from .request import OrmSelectRequest, OrmInsertRequest, OrmUpdateRequest, OrmDeleteRequest
from .results import OrmRawResult
from .manage import manager
from .attributes.base import ColumnAttributeAbstract
from .attributes.relationships import ManyToMany
from .values.base import AttributeValueAbstract
from .attributes.keys import compare_keys


# noinspection PyTypeChecker
class OrmSessionAbstract(object):
    """
    Abstract session class, must not be used in the end project.
    The session is the one connection to the DBMS within which requests are executed.
    """
    dbms_type = 'unknown'

    def __init__(self, host, dbname, username, password, port=None, tag=None, debug=None):
        """
        :host                       Database engine host name or IP;
        :dbname                     Database name on the database engine;
        :username                   Username which will be used to connect to the database;
        :password                   Corresponding password for the user above;
        :port                       Custom TCP port number if it is not the standard one;
        :tag                        Tag for this session (see documentation);
        :debug                      A set of debug flags, defaults to None;
        """
        self.dbms_host = host
        self.dbms_dbname = dbname
        self.dbms_username = username
        self.dbms_password = password
        self.dbms_port = port
        self.tag = tag
        self.cn = None
        self.cr = None
        self.time_zone = None
        self.dt_format = None
        self.session_user = False
        self.session_rls = False
        self.opened = False
        self.debug = debug if debug is not None else manager.get_debug()
        self.is_migrating = False
        self.open()

    def _check_opened(self):
        """ Ensures that session's connection been opened, raises an Exception otherwise. """
        if not self.opened:
            raise OrmException("The session is defined, but connection did not opened using `open` method!")

    @staticmethod
    def quote_name(value):  # Abstract
        pass

    def open(self):  # Abstract
        pass

    def close(self):
        """ Closes the previously opened connection to the DBMS. Doing nothing
        if connection did not established (method `open` did not called). """
        if not self.opened:
            return
        if self.cr:
            self.cr.close()
        if self.cn:
            self.cn.close()
        self.opened = False

    def set_time_zone(self, time_zone):
        """ Used to set_value the time zone on the DBMS side for this connection session.
        :time_zone                  (str) The time zone. Use DBMS correct known time zone.
                                    (None) If 'None' - reset DBMS time zone to the global default.
        """
        self._check_opened()
        self.time_zone = time_zone
        # TODO! Check PostgreSQL timezone syntax
        if self.time_zone is None:
            self.execute("SET time_zone = @@global.time_zone")
        else:
            self.execute("SET time_zone=%(time_zone)s", {'time_zone': self.time_zone})

    def set_session_user(self, user):
        """ Sets this session working user. The user here is not the database connection user used
        to deal with DBMS, but the representation of the information system's (which is using this
        ORM) user.
        :user                       (object instance) May be set to the corresponding Model's instance,
                                    (int|str) or may be set to the corresponding value of the primary
                                    key identifying the session user.
        """
        self.session_user = user

    def inqure_session_user(self):
        """
        :returns                    (None) if no session user is set;
                                    Value of the current session's user's primary key;
        """
        from .models.base import OrmModel
        if not self.session_user:
            return None
        if isinstance(self.session_user, OrmModel):
            _pk = self.session_user.__pk__.copy()
            pk = _pk.popitem()
            return pk[1]
        return self.session_user

    def begin(self):
        """ Begins transaction. `START TRANSACTION` using database library interface. """
        self._check_opened()
        self.cn.begin()

    def rollback(self):
        """ Rolls back the last transaction. `ROLLBACK` using database library interface. """
        self._check_opened()
        self.cn.rollback()

    def commit(self):
        """ Commits the transaction. `COMMIT` using database library interface. """
        self._check_opened()
        self.cn.commit()

    @staticmethod
    def _repr_query_params(p):
        """
        :returns                    Query parameters textual represented as Name=>Value
        """
        return ",  ".join([("%s=>%r" % (k, p[k])) for k in sorted(p.keys())])

    def execute(self, request, parameters=None):
        """ Executes the raw SQL query which not returning anything. Parameters in the
        query may be used using s(parameter_name)% format.
        :request                    Textual raw SQL query to execute to;
        :parameters                 [dict] with parameters for the query;
        """
        if not request:
            return
        if parameters is not None and not isinstance(parameters, dict):
            raise OrmParameterError("OrmSessionAbstract.query parameters must be set using dict() type!")
        if not manager.handle_query(request, parameters):
            print("DECLINED by handler: " + request)
            return
        rql = request.lower()
        do_debug = self.debug is True \
            or (isinstance(self.debug, (list, tuple))
                and (
                    ('select' in self.debug and (rql[:6] == 'select' or rql[:7] == '(select') and not self.is_migrating)
                    or ('migrate-getstruct' in self.debug and rql[:6] == 'select' and self.is_migrating)
                    or ('modify' in self.debug and rql[:6] in ('insert', 'update', 'delete'))
                    or ('alter' in self.debug and rql[:4] in ('crea', 'alte', 'drop'))
                ))
        if do_debug:
            print("")
            print(">> %s" % request)
        if parameters:
            p_ = dict()
            for k in parameters:
                v = parameters[k]
                v_ = v.value if isinstance(v, AttributeValueAbstract) else v
                p_[k] = v_
            parameters = p_
            if do_debug:
                print("@@ %s" % self._repr_query_params(parameters))
        self.cr.execute(request, parameters)
        if do_debug:
            print("")

    def query(self, request, parameters=None):
        """ Executes the raw SQL query and return `OrmRawResult` instance with results
        of the query. Parameters in the query may be used using s(parameter_name)% format.
        The results must be taken using '.all()' or '.one()' methods of the 'OrmRawResult'
        instance.
        :request                    Textual raw SQL query to execute to;
        :parameters                 [dict] with parameters for the query;
        :returns                    (OrmRawResult) results of the qurry.
        """
        self.execute(request, parameters)
        r = OrmRawResult(self.cr)
        # if self.debug is True or (isinstance(self.debug, str) and 'query-results' in self.debug):
        #     print("R<< %r" % r)
        #     print("|")
        return r

    def add(self, *args):
        """ Assigns specified object instance(s) with this session. """
        from .models.base import OrmModelAbstract
        for arg in args:
            if not isinstance(arg, OrmModelAbstract):
                raise OrmParameterError("`session`.add() method requires object instance(s) to be given!")
            arg.__session__ = self

    def new(self, model, *args, **kwargs):
        """ Creates a new object instance of given 'model' type and automatically assigns it with
        this session.
        :model                      (OrmModel) the model class instance of which to create;
        :*args, **kwargs            Optional parameters to pass to the creating instance;
        :returns                    (object instance) newly created object instance of given
                                    Model and already assigned with this session.
        """
        instance = model(*args, **kwargs)
        instance.__session__ = self
        return instance

    def select(self, *args, **kwargs):
        """ Selects from the database objects by given criteria.
        :returns                    (OrmSelectRequest) object ready to execute by .go() method.
        """
        from .models.views import OrmView
        kwargs['session'] = self
        _view = None
        _args = list()
        for arg in args:
            if not inspect.isclass(arg) or not issubclass(arg, OrmView):
                _args.append(arg)
                continue
            if _view is not None:
                raise OrmParameterError(
                    "can select from only one OrmView, several given!"
                )
            _view = arg
        if _view is not None:
            return _view.request(*_args, **kwargs)
        return OrmSelectRequest(*args, **kwargs)

    def insert(self, *args, **kwargs):
        """ Inserts given object instances in the database using this session and INSERT command.
        :returns                    (OrmInsertRequest) object ready to execute by .go() method.
        """
        kwargs['session'] = self
        return OrmInsertRequest(*args, **kwargs)

    def update(self, *args, **kwargs):
        """ Updates given object instances in the database using this session and UPDATE command.
        :returns                    (OrmUpdateRequest) object ready to execute by .go() method.
        """
        kwargs['session'] = self
        return OrmUpdateRequest(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """ Deletes given object instances from the database using this session.
        :returns                    (OrmDeleteRequest) object ready to execute by .go() method.
        """
        kwargs['session'] = self
        return OrmDeleteRequest(*args, **kwargs)

    def write(self, *args, **kwargs):
        """ Writes given object instances to the database using this session. This method
        determines itself what to do - do INSERT or do UPDATE, so it is preferred against
        update() or insert() methods.
        """
        from .models.base import OrmModelAbstract
        kwargs['session'] = self
        for arg in args:
            if not isinstance(arg, OrmModelAbstract):
                raise OrmParameterError("session.write() method requires an object instance(s) to be given!")
            arg.write(**kwargs)

    def find(self, model, what, **kwargs):
        """
        Finds over objects for the given Model, returning found objects if any. Which attributes
        of the Model uses when looking for given phrase declares at Model declaration.
        :model                      (OrmModel) Model over objects of which type to search to;
        :what                       (str) Textual string what to find to;
        :returns                    (OrmSearchRequest) object ready to execute by .go() method.
        """
        from .request import OrmSearchRequest
        from .models.views import OrmView
        if issubclass(model, OrmView):
            return model.find(what, session=self, **kwargs)
        return OrmSearchRequest(model, what, session=self, **kwargs)

    def get_table_struct(self, table):  # Abstract
        pass

    def is_model_table_exists(self, model):  # Abstract
        pass

    def get_database_tables(self):  # Abstract
        pass

    def create_model_table(self, model, apply=True, restrict_new_fk=False):  # Abstract
        pass

    def alter_model_table(self, model, table_struct=None, drop=False, alter_foreign_keys=True):  # Abstract
        pass

    def create_model_foreign_keys(self, model):  # Abstract
        pass

    def drop_table_foreign_keys(self, tablename, tbl_struct_fks):  # Abstract
        pass

    def drop_model_table(self, model, apply=True):  # Abstract
        pass

    def migrate(self, drop=False, upload_initial=True):
        """ Migrates the database schema - all defined and written in the `mapper` real models - creating
        and modifying database at DBMS to confort to defined models.
        :drop                       [bool] Do drop columns which are not defined in altering Models;
        :upload_initial             [bool] Do upload initial data to the newly creating Models'
                                    tables, if any defined;
        """

        # Handling debugging rules
        self.is_migrating = True

        # Validating everything before continue (we must be sure that all elements are
        # correct and validated prior to database altering)
        mapper.validate_all()

        # Retrieving models for migration (excluding virtual models, like views and templates)
        models = mapper.get_models_for_migrate(self.tag)

        # Getting the list of existing tables
        existing_tables = self.get_database_tables()

        # Going through all defined models and filling up two lists - tables to be created
        # and tables to be altered.
        to_create = list()
        to_verify = list()
        to_drop = list()
        to_alter = dict()
        for name in models:
            model = models[name]
            if model.table in existing_tables:
                to_verify.append(name)
            else:
                to_create.append(name)

        # Stage 1. Retrieving structure of existing tables in the database by
        # declared models.
        tbl_struct = dict()
        for tablename in existing_tables:
            tbl_struct[tablename] = self.get_table_struct(tablename)

        # Stage 2. Analysing existing models to understand - do we need to
        # migrate something. We about to drop foreign keys prior to any
        # modifications because otherwise existing key may deny some actions
        # on existing tables.
        for name in to_verify:
            model = models[name]
            tablename = model.table
            queries = self.alter_model_table(model, tbl_struct[tablename], drop=drop, alter_foreign_keys=False)
            if not queries:
                continue
            to_alter[name] = queries

        # If no alter requests are present, and no new tables to be created
        # or existing tables to be dropped - returning.
        if not to_create and not to_alter and not to_drop:
            self.is_migrating = False
            return

        # Stage 3. If something is about to be done - dropping foreign keys
        # for affecting models first.
        for name in to_alter:
            model = models[name]
            tablename = model.table
            query = self.drop_table_foreign_keys(tablename, tbl_struct[tablename]['foreign_keys'])
            if not query:
                continue
            self.execute(query)

        # Stage 4. Create new tables, but not create foreign keys for them
        for name in to_create:
            model = models[name]
            self.create_model_table(model, apply=True, restrict_new_fk=True)

        # Stage 5. Uploading initial objects into newly created tables
        m2m_initial = dict()
        if upload_initial:
            for name in to_create:
                model = models[name]
                initial_objects = model.__meta__.initial
                if not initial_objects:
                    continue
                for d in initial_objects:
                    instance = model()
                    instance.__session__ = self
                    instance.__initialize_from__(**d)
                    instance.write(session=self, initial=True)
                    # Finding Many-To-Many attributes and adding data of them to
                    # initialize a little later
                    for k in d:
                        c = getattr(model, k, None)
                        if c is None or not isinstance(c, ManyToMany):
                            continue
                        objects_assigned = d[k]
                        if not isinstance(objects_assigned, (list, tuple)):
                            raise OrmModelDeclarationError(
                                "Many-To-Many assignments in __initial__ must be set using (list|tuple) type!"
                            )
                        c.validate()
                        if c.key not in m2m_initial:
                            m2m_initial[c.key] = {
                                'jmodel': c.junction_model,
                                'rows': []
                            }
                        f_model_name = c.key[0] if c.key[1] == model.__name__ else c.key[1]
                        l_columns = c.junction_model.__m2m_columns__[model.__name__]
                        f_columns = c.junction_model.__m2m_columns__[f_model_name]
                        f_keys = dict()
                        for c_ in f_columns:
                            f_keys[c_.parent_model_k] = c_.model_k
                        for oa in objects_assigned:
                            j_keys = dict()
                            for c_ in l_columns:
                                j_keys[c_.model_k] = instance.__getforwrite__(c_.parent_model_k, self)
                            if isinstance(oa, (int, str, float)):
                                if len(f_columns) != 1:
                                    raise OrmModelDeclarationError(
                                        "Many-To-Many assignment in __initial__ has simple format specified"
                                        " for the foreign object's primary key value, but foreign object's"
                                        " Model has complex primary key defined!"
                                    )
                                j_keys[f_columns[0].model_k] = oa
                            elif isinstance(oa, dict):
                                for oa_k in oa:
                                    if oa_k not in f_keys:
                                        raise OrmModelDeclarationError(
                                            "unknown Many-To-Many key '%s' in __initial__ for %s!"
                                            % (oa_k, str(c.key))
                                        )
                                    oa_v = oa[oa_k]
                                    j_keys[f_keys[oa_k]] = oa_v
                            else:
                                raise OrmModelDeclarationError(
                                    "Many-To-Many assignments in __initial__ must be set using dict "
                                    " of corresponding attributes' keys-values of foreign Model's primary"
                                    " key or using corresponding single value. (for example: {...'attrname':"
                                    " ['1', '2', '3'], ...} means that this object will be associated with"
                                    " foreign objects with primary key values 1, 2 and 3; or"
                                    " {...'attrname': [{'id': 1}, {'id': 2}, {'id: 3}], ...} - means the"
                                    " same)."
                                )
                            if j_keys in m2m_initial[c.key]['rows']:
                                continue
                            m2m_initial[c.key]['rows'].append(j_keys)

        # Stage 5a. Writting collected in the Stage 5 many to many relationships
        for m2m_key in m2m_initial:
            m2m = m2m_initial[m2m_key]
            m2m_jmodel = m2m['jmodel']
            m2m_rows = m2m['rows']
            for row in m2m_rows:
                jinstance = m2m_jmodel()
                for k_ in row:
                    setattr(jinstance, k_, row[k_])
                jinstance.write(session=self, all_attrs=True)

        # Stage 6. Alter existing tables, again, without any foreign key
        # affecting
        for name in to_alter:
            queries = to_alter[name]
            if queries is True:
                continue
            for query in queries:
                self.execute(query)

        # Stage 7. Create foreign keys for newly created tables
        for name in to_create:
            model = models[name]
            query = self.create_model_foreign_keys(model)
            if not query:
                continue
            self.execute(query)
        for name in to_alter:
            model = models[name]
            query = self.create_model_foreign_keys(model)
            if not query:
                continue
            self.execute(query)

        # Stage 8. Commiting changes (not necessary for MySQL, for example, but is
        # required for PostgreSQL, for example)
        self.commit()

        # Reseting debugging rules
        self.is_migrating = False


class MysqlSession(OrmSessionAbstract):
    dbms_type = 'mysql'

    @staticmethod
    def quote_name(value):
        return '`' + value + '`'

    def open(self):
        """ Opens the connection to the DBMS using stored at a time of class instance
        creation parameters like host, username, password and etc. """
        import MySQLdb
        self.cn = MySQLdb.connect(host=self.dbms_host,
                                  user=self.dbms_username,
                                  passwd=self.dbms_password,
                                  db=self.dbms_dbname,
                                  port=self.dbms_port or 3306,
                                  charset='utf8',
                                  use_unicode=True,
                                  client_flag=2)
        self.cr = self.cn.cursor()
        self.opened = True
        self.execute("SET NAMES 'utf8'")

    def get_table_struct(self, table):
        """ Reads the table structure from DBMS of the OrmModel. Reads attributes definitions and keys,
        including indexes, primary keys, foreign keys, unique keys, etc.
        :table                      (str) The existing database table name;
        :returns                    (dict) The existing database table structure.
        """
        keys = {}
        columns = {}
        indexes = {}
        foreign_keys = {}
        unique_keys = {}
        pk = []

        tablename = table if isinstance(table, str) else table.__table__

        # Selecting attributes definitions from INFORMATION_SCHEMA, basing on MySQL documentation
        # "22.4 The INFORMATION_SCHEMA COLUMNS Table"
        query = ("SELECT COLUMN_NAME, COLUMN_DEFAULT, IS_NULLABLE, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH,"
                 " CHARACTER_OCTET_LENGTH, NUMERIC_PRECISION, NUMERIC_SCALE, DATETIME_PRECISION,"
                 " CHARACTER_SET_NAME, COLLATION_NAME, COLUMN_TYPE, COLUMN_KEY, EXTRA"
                 " FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=%(ts)s AND TABLE_NAME=%(tn)s")
        dbr = self.query(query, {'ts': self.dbms_dbname, 'tn': tablename}).all()
        if not dbr:
            return None
        for r in dbr:
            c = dict()
            c_name = str(r[0])
            c['column_name'] = c_name
            c['column_default'] = r[1]
            c['is_nullable'] = True if str(r[2]).upper() == 'YES' else False
            c['data_type'] = str(r[3]).lower()
            c['character_maximum_length'] = r[4]
            c['character_octet_length'] = r[5]
            c['numeric_precision'] = r[6]
            c['numeric_scale'] = r[7]
            c['datetime_precision'] = r[8]
            c['character_set_name'] = str(r[9]).lower() if r[9] is not None else None
            c['collation_name'] = str(r[10]).lower() if r[10] is not None else None
            c['column_type'] = str(r[11]).lower()
            c['column_key'] = r[12]
            c['extra'] = str(r[13]).lower() if r[13] is not None else None
            columns[c_name] = c

        # Selecting informations about declared keys usage, basing on MySQL documentation
        # "22.11 The INFORMATION_SCHEMA KEY_COLUMN_USAGE Table"
        query = ("SELECT CONSTRAINT_NAME, COLUMN_NAME, ORDINAL_POSITION, POSITION_IN_UNIQUE_CONSTRAINT,"
                 " REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE"
                 " WHERE CONSTRAINT_SCHEMA = %(ts)s AND TABLE_NAME = %(tn)s"
                 " ORDER BY POSITION_IN_UNIQUE_CONSTRAINT, ORDINAL_POSITION")
        dbr = self.query(query, {'ts': self.dbms_dbname, 'tn': tablename}).all()
        if dbr:
            for r in dbr:
                key = dict()
                key_name = str(r[0])
                if key_name.upper() == 'PRIMARY' and r[1]:
                    # PRIMARY KEY part
                    pk.append(r[1])
                    continue
                if key_name in keys:
                    # Composite key part
                    keys[key_name]['_col_aliases'].append(r[1])
                    if r[5] is not None:
                        keys[key_name]['referenced_columns'].append(r[5])
                    continue
                # Defining a new key
                key['constraint_name'] = key_name
                # Basing on MySQL documentation: "22.11 The INFORMATION_SCHEMA KEY_COLUMN_USAGE Table"
                # the `POSITION_IN_UNIQUE_CONSTRAINT` column is NULL for UNIQUE KEYs and PRIMARY KEYs
                # and is not NULL for FOREIGN KEYs.
                key['is_foreign_key'] = r[3] is not None
                key['referenced_table_name'] = r[4]
                key['referenced_columns'] = [r[5], ] if r[5] is not None else []
                key['on_update'] = None
                key['on_delete'] = None
                key['_col_aliases'] = [r[1], ]
                keys[key_name] = key

        # Additionally selecting information about referential constraints - foreign keys. Doing it
        # by selecting from REFERENTIAL_CONSTRAINTS basing on MySQL documentation
        # "22.19 The INFORMATION_SCHEMA REFERENTIAL_CONSTRAINTS Table"
        query = ("SELECT CONSTRAINT_NAME, UPDATE_RULE, DELETE_RULE FROM"
                 " INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS WHERE"
                 " CONSTRAINT_SCHEMA = %(ts)s AND TABLE_NAME = %(tn)s")
        dbr = self.query(query, {'ts': self.dbms_dbname, 'tn': tablename}).all()
        if dbr:
            for r in dbr:
                fk_name = r[0]
                if fk_name not in keys:
                    continue
                keys[fk_name]['is_foreign_key'] = True
                keys[fk_name]['on_update'] = r[1]
                keys[fk_name]['on_delete'] = r[2]

        # Handling got keys
        if keys:
            for name in keys:
                # We about to define three general types of keys:
                # a) PRIMARY KEY
                # b) FOREIGN KEY
                # c) UNIQUE KEY
                # INDEX KEY (or just a KEY in terms of MySQL) are stored
                # separatelly, so will not be found in general KEYS structure.
                # The first type (a) - the PRIMARY KEY (even composite)
                # detects in the procedure above and not stored in the general
                # `keys` variable, so this is not a point to work with PK here.
                key = keys[name]
                is_fk = key['is_foreign_key']
                if is_fk:
                    fk = {
                        'constraint_name': key['constraint_name'],
                        'model_idx_columns': key['_col_aliases'],
                        'ref_idx_columns': key['referenced_columns'],
                        'ref_table': key['referenced_table_name'],
                        'on_update': key['on_update'],
                        'on_delete': key['on_delete']
                    }
                    foreign_keys[name] = fk
                else:
                    uk = {
                        'constraint_name': key['constraint_name'],
                        '_col_aliases': key['_col_aliases']
                    }
                    unique_keys[name] = uk

        # Selecting information about INDEX KEYs, basing on MySQL documentation
        # "22.23 The INFORMATION_SCHEMA STATISTICS Table"
        query = ("SELECT INDEX_NAME, COLUMN_NAME, SUB_PART FROM INFORMATION_SCHEMA.STATISTICS"
                 " WHERE TABLE_SCHEMA = %(ts)s AND TABLE_NAME = %(tn)s")
        dbr = self.query(query, {'ts': self.dbms_dbname, 'tn': tablename}).all()
        if dbr:
            for r in dbr:
                name = r[0]
                # If the index key is already registered in the `keys` varitable - skipping
                # due this is not a index key.
                if name in keys or name.upper() == 'PRIMARY':
                    continue
                # If a composite index key part is found
                if name in indexes:
                    indexes[name]['_col_aliases'].append((r[1], r[2]))
                    indexes[name]['column_names'].append(r[1])
                    continue
                # Defining the new index key
                indexes[name] = {
                    'key_name': name,
                    '_col_aliases': [(r[1], r[2]), ],
                    'column_names': [r[1], ]
                }

        # Accumulating the resulting information about model's table definition
        table_struct = {
            'columns': columns,
            'indexes': indexes,
            'foreign_keys': foreign_keys,
            'unique_keys': unique_keys,
            'primary_key': pk
        }
        return table_struct

    def is_model_table_exists(self, model):
        """ Checks is the OrmModel's table existance in the database.
        :model                      (OrmModel) The Model for which to search for database table
                                    existabce to;
        :returns                    True if the corresponding database table is exists, False
                                    otherwise.
        """
        q = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = %(ts)s AND TABLE_NAME = %(tn)s"
        r = self.query(q, {'tn': str(model.table), 'ts': self.dbms_dbname}).one()
        if not r:
            return False
        return str(r[0]) == str(model.table)

    def create_model_table(self, model, apply=True, restrict_new_fk=False):
        """ Creates a table in the database. Raises an exeption if the table is already
        exists in the database. Use `alter` instead to automatically migrate the database
        schema (do create or alter the table).
        :model                      (OrmModel) The corresponding Model for which database table to
                                    create to;
        :apply                      [bool] If set to True - automatically executes the ALTER query,
                                    if not - only returns the SQL query;
        :restrict_new_fk            [bool] If set to True - foreign keys will not be created right
                                    after database table creation; otherwise (default) - corresponding
                                    CREATE FOREIGN KEY procedures will be planned;
        :returns                    (str) Resulting SQL query.
        """
        if self.is_model_table_exists(model):
            raise Exception("Cannot CREATE TABLE because it is already exists: `%s`" % model.__table__)
        columns = model.__meta__.get_column_attributes()
        c_def = []
        for c in columns:
            q = c.declaration_sql(self)
            c_def.append("`%s` %s" % (c.tbl_k, q))
        q_def = ", ".join(c_def)
        if model.__meta__.primary_key:
            pkc = []
            for c in model.__meta__.get_primary_key():
                pkc.append("`%s`" % c.tbl_k)
            q_pk = "PRIMARY KEY (%s)" % (", ".join(pkc))
            q_def += ", " + q_pk
        foreign_keys = model.__meta__.get_foreign_keys()
        if foreign_keys and not restrict_new_fk:
            fks = []
            for fk in foreign_keys:
                fks.append(fk.declaration_sql(self))
            q_fk = ", ".join(fks)
            q_def += ", " + q_fk
        unique_keys = model.__meta__.get_unique_keys()
        if unique_keys:
            uks = []
            for uk in unique_keys:
                uks.append(uk.declaration_sql(self))
            q_uk = ", ".join(uks)
            q_def += ", " + q_uk
        index_keys = model.__meta__.get_index_keys()
        if index_keys:
            iks = []
            for ik in index_keys:
                iks.append(ik.declaration_sql(self))
            q_ik = ", ".join(iks)
            q_def += ", " + q_ik
        query = "CREATE TABLE `%s` (%s) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin" % (model.table, q_def)
        if apply:
            self.execute(query)
        return query

    def alter_model_table(self, model, table_struct=None, drop=False, alter_foreign_keys=True):
        """ Returns a SQL query to alter database table basing on the declared Model.
        :model                      (OrmModel) the Model for which corresponding
                                    database table to alter;
        :table_struct               [dict] containing the current corresponding table structure
                                    at the database; if not set - current table structure will
                                    be automatically loaded by this method;
        :drop                       [bool] If set to True - columns in the database table which
                                    are not exists in the Model will be dropped; otherwise
                                    (default) - will be kept not touched;
        :alter_foreign_keys         [bool] If set to True (default) - foreign keys will be altered
                                    right in place of this alter procedure; otherwise this method
                                    will not worry about dropping and creating foreign keys;
        :returns                    (str) The resulting query.
        """
        if not table_struct:
            table_struct = self.get_table_struct(model.table)
        model_struct = model.__meta__.get_model_struct()

        _q_to_alter = []
        _fk_to_drop = []

        # Columns
        for k in model_struct['columns']:
            c = model_struct['columns'][k]
            tbl_k = c.tbl_k
            if not isinstance(c, ColumnAttributeAbstract):
                continue
            # If the column not exists at all - just add it in the alter procedure
            if tbl_k not in table_struct['columns']:
                add_sql = c.declaration_sql(self)
                q = "ADD `%s` %s" % (tbl_k, add_sql)
                _q_to_alter.append(q)
                continue
            # If the column exists - we have to compare it's model definition with
            # database table definition and make changes in the alter procedure
            # if some differences will be found.
            tbl_c = table_struct['columns'][tbl_k]
            if not c.is_eq_with_tbl_schema(tbl_c, self):
                alter_sql = c.declaration_sql(self)
                q = "CHANGE `%s` `%s` %s" % (tbl_k, tbl_k, alter_sql)
                _q_to_alter.append(q)
                # Checking - is this column using in foreign keys - and mark those
                # foreign keys where this column is using to drop prior to the
                # column been modified.
                for fk_name in table_struct['foreign_keys']:
                    if fk_name in _fk_to_drop:
                        continue
                    key = table_struct['foreign_keys'][fk_name]
                    if tbl_k not in key['model_idx_columns']:
                        continue
                    _fk_to_drop.append(fk_name)

        # Primary key
        t_pk = table_struct['primary_key']
        m_pk = model_struct['primary_key']
        if not compare_keys(t_pk, m_pk):
            cs = []
            for c in m_pk:
                cs.append("`%s`" % str(c.tbl_k))
            q = "" if not t_pk else "DROP PRIMARY KEY, "
            q += "ADD PRIMARY KEY(%s)" % ",".join(cs)
            _q_to_alter.append(q)

        # Unique keys
        t_uks = table_struct['unique_keys']
        m_uks = model_struct['unique_keys']
        keep_uks = []
        add_uks = []
        for k in m_uks:
            m_key = m_uks[k]
            if m_key.tbl_k not in t_uks:
                add_uks.append(m_key)
                continue
            t_key = t_uks[m_key.tbl_k]
            if not compare_keys(t_key['_col_aliases'], m_key.columns):
                add_uks.append(m_key)
            else:
                keep_uks.append(m_key.tbl_k)
        for tbl_k in t_uks:
            if tbl_k in keep_uks:
                continue
            q = "DROP KEY `%s`" % str(tbl_k)
            _q_to_alter.append(q)
        for c in add_uks:
            _q_to_alter.append("ADD %s" % c.declaration_sql(self))

        # Index keys
        t_ixs = table_struct['indexes']
        m_ixs = model_struct['indexes']
        keep_ixs = []
        add_ixs = []
        for k in m_ixs:
            m_key = m_ixs[k]
            if m_key.tbl_k not in t_ixs:
                add_ixs.append(m_key)
                continue
            t_key = t_ixs[m_key.tbl_k]
            if not compare_keys(t_key['column_names'], m_key.columns):
                add_ixs.append(m_key)
            else:
                keep_ixs.append(m_key.tbl_k)
        for tbl_k in t_ixs:
            if tbl_k in keep_ixs:
                continue
            q = "DROP KEY `%s`" % str(tbl_k)
            _q_to_alter.append(q)
        for c in add_ixs:
            _q_to_alter.append("ADD %s" % c.declaration_sql(self))

        # Foreign keys
        t_fks = table_struct['foreign_keys']
        m_fks = model_struct['foreign_keys']
        keep_fks = []
        add_fks = []
        for k in m_fks:
            m_key = m_fks[k]
            m_key.validate()
            if m_key.tbl_k not in t_fks or m_key.tbl_k in _fk_to_drop:
                add_fks.append(m_key)
                continue
            t_key = t_fks[m_key.tbl_k]
            if t_key['ref_table'] != m_key.ref_model.table \
                    or len(t_key['model_idx_columns']) != len(m_key.columns) \
                    or len(t_key['ref_idx_columns']) != len(m_key.ref_columns):
                add_fks.append(m_key)
                continue
            do_continue = False
            for i in xrange(len(m_key.columns)):
                if t_key['model_idx_columns'][i] == getattr(m_key.model, m_key.columns[i]).tbl_k:
                    continue
                add_fks.append(m_key)
                do_continue = True
                break
            if do_continue:
                continue
            for i in xrange(len(m_key.ref_columns)):
                if t_key['ref_idx_columns'][i] == getattr(m_key.ref_model, m_key.ref_columns[i]).tbl_k:
                    continue
                add_fks.append(m_key)
                do_continue = True
                break
            if do_continue:
                continue
            t_key_on_delete = str(t_key['on_delete']).upper()
            m_key_on_delete = 'RESTRICT' if m_key.on_delete is None else str(m_key.on_delete).upper()
            if t_key_on_delete != m_key_on_delete:
                add_fks.append(m_key)
                continue
            t_key_on_update = str(t_key['on_update']).upper()
            m_key_on_update = 'RESTRICT' if m_key.on_update is None else str(m_key.on_update).upper()
            if t_key_on_update != m_key_on_update:
                add_fks.append(m_key)
                continue
            keep_fks.append(m_key.tbl_k)
        for tbl_k in t_fks:
            if tbl_k in keep_fks or tbl_k in _fk_to_drop:
                continue
            _fk_to_drop.append(tbl_k)
        need_alter_foreign_keys = len(add_fks) != 0
        if alter_foreign_keys:
            for c in add_fks:
                _q_to_alter.append("ADD %s" % c.declaration_sql(self))
                _q_to_alter.append("ADD %s" % c.declaration_key_sql(self))

        # If nothing to do - just returning None
        if not _q_to_alter and not _fk_to_drop and not need_alter_foreign_keys:
            return None

        queries = list()
        # If we have foreign keys to be dropped prior to other ALTER actions,
        # including adding changed version of those foreign keys - put drops
        # in front of all other actions here
        if _fk_to_drop and alter_foreign_keys:
            q_fk_drop = []
            for fk_name in _fk_to_drop:
                q_fk_drop.append("DROP FOREIGN KEY `%s`" % str(fk_name))
                q_fk_drop.append("DROP KEY `%s`" % str(fk_name))
            dfk_query = "ALTER TABLE `%s` %s" % (model.table, ", ".join(q_fk_drop))
            queries.append(dfk_query)

        # Composing SQL ALTER request
        query = "ALTER TABLE `%s` %s" % (model.table, ", ".join(_q_to_alter)) if _q_to_alter else ""
        if query:
            queries.append(query)

        # If only we need - is to alter foreign keys
        if not queries and need_alter_foreign_keys:
            return True

        # Returning prepared queries
        return queries

    def create_model_foreign_keys(self, model):
        """ Returns a SQL query to create foreign keys for the database table
        basing on the declared Model.
        :model                      (OrmModel) the Model for which corresponding
                                    database table to create foreign keys for;
        :returns                    (str) The resulting query.
        """
        query = ""
        foreign_keys = model.__meta__.get_foreign_keys()
        if foreign_keys:
            fks = []
            for fk in foreign_keys:
                fks.append("ADD %s" % fk.declaration_sql(self))
                fks.append("ADD %s" % fk.declaration_key_sql(self))
            query = ", ".join(fks)
        if query:
            query = "ALTER TABLE `%s` %s" % (model.table, query)
        return query

    def drop_table_foreign_keys(self, tablename, tbl_struct_fks):
        """ Returns a SQL query to drop foreign keys for the database table.
        :tablename                  (str) The name of the datbase table;
        :tbl_struct_fks             (dict) Existing foreign keys struct;
        :returns                    (str) The resulting query.
        """
        if not tbl_struct_fks:
            return None
        queries = list()
        for fk_name in tbl_struct_fks:
            constraint_name = tbl_struct_fks[fk_name]['constraint_name']
            queries.append("DROP FOREIGN KEY `%s`" % str(constraint_name))
            queries.append("DROP KEY `%s`" % str(constraint_name))
        return "ALTER TABLE `%s` %s" % (tablename, ", ".join(queries))

    def drop_model_table(self, model, apply=True):
        """ Drops the model's table from the database.
        :apply          (bool) If set_value to True - automatically executes the ALTER query, if
                        not - only returns the SQL query.
        :returns        (str) SQL query for DROPing the table.
        """
        if not self.is_model_table_exists(model):
            raise Exception("Cannot DROP table because it is not exists: `%s`!" % model.__table__)
        pass

    def get_database_tables(self):
        """
        :returns                    (list) A list of table names in the current database.
        """
        q = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = %(ts)s"
        dbr = self.query(q, {'ts': self.dbms_dbname}).all()
        existing_tables = []
        for r in dbr:
            existing_tables.append(r[0])
        return existing_tables


class PostgresqlSession(OrmSessionAbstract):
    """
    PostgreSQL session class
    """
    dbms_type = 'postgresql'

    def __init__(self, host, dbname, username, password, port=None, tag=None, schema='public', debug=None):
        self.dbms_schema = schema
        super(PostgresqlSession, self).__init__(host=host, dbname=dbname, username=username, password=password,
                                                port=port, tag=tag, debug=debug)

    @staticmethod
    def quote_name(value):
        return '"' + value + '"'

    def open(self):
        """ Opens the connection to the DBMS using stored at a time of class instance
        creation parameters like host, username, password and etc. """
        import psycopg2
        self.cn = psycopg2.connect(host=self.dbms_host,
                                   user=self.dbms_username,
                                   password=self.dbms_password,
                                   dbname=self.dbms_dbname,
                                   port=self.dbms_port or 5432)
        self.cr = self.cn.cursor()
        self.opened = True
        self.execute("SET NAMES 'utf8'")
        if self.dbms_schema != 'public':
            self.execute("SET search_path TO '%s'" % self.dbms_schema)

    def get_table_struct(self, table):
        """ Reads the table structure from DBMS of the OrmModel. Reads attributes definitions and keys,
        including indexes, primary keys, foreign keys, unique keys, etc.
        :table                      (str) The existing database table name;
        :returns                    (dict) The existing database table structure.
        """
        keys = {}
        columns = {}
        indexes = {}
        foreign_keys = {}
        unique_keys = {}
        pk = []
        pk_keynames = []

        tablename = table if isinstance(table, str) else table.__table__

        # Selecting attributes definitions from INFORMATION_SCHEMA, basing on PostgreSQL documentation
        # "34.15. The Information Schema.columns"
        query = ("SELECT COLUMN_NAME, COLUMN_DEFAULT, IS_NULLABLE, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH,"
                 " CHARACTER_OCTET_LENGTH, NUMERIC_PRECISION, NUMERIC_SCALE, DATETIME_PRECISION, UDT_NAME"
                 " FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=%(ts)s AND TABLE_NAME=%(tn)s")
        dbr = self.query(query, {'ts': self.dbms_schema, 'tn': tablename}).all()
        if not dbr:
            return None
        for r in dbr:
            c = dict()
            c_name = str(r[0])
            c['column_name'] = c_name
            c['column_default'] = r[1]
            c['is_nullable'] = True if str(r[2]).upper() == 'YES' else False
            c['data_type'] = str(r[3]).lower()
            c['character_maximum_length'] = r[4]
            c['character_octet_length'] = r[5]
            c['numeric_precision'] = r[6]
            c['numeric_scale'] = r[7]
            c['datetime_precision'] = r[8]
            c['character_set_name'] = None
            c['collation_name'] = None
            c['column_type'] = str(r[9]).lower()
            c['column_key'] = None
            c['extra'] = None
            columns[c_name] = c

        # Selecting informations about declared keys usage, basing on PostgreSQL documentation
        # "34.30 The Information Schema.key_column_usage"
        query = (
            "SELECT tc.CONSTRAINT_NAME, kcu.COLUMN_NAME, tc.CONSTRAINT_TYPE"
            " FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc"
            " JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu"
            " ON kcu.CONSTRAINT_NAME = tc.CONSTRAINT_NAME"
            " WHERE tc.CONSTRAINT_SCHEMA=%(ts)s AND tc.TABLE_NAME=%(tn)s"
            " AND UPPER(tc.CONSTRAINT_TYPE) IN ('PRIMARY KEY', 'FOREIGN KEY', 'UNIQUE')"
            " ORDER BY kcu.CONSTRAINT_NAME, kcu.POSITION_IN_UNIQUE_CONSTRAINT, kcu.ORDINAL_POSITION"
        )
        dbr = self.query(query, {'ts': self.dbms_schema, 'tn': tablename}).all()
        if dbr:
            for r in dbr:
                key = dict()
                key_name = str(r[0])
                key_type = str(r[2]).upper()
                if key_type == 'PRIMARY KEY' and r[1]:
                    # PRIMARY KEY part
                    pk.append(r[1])
                    pk_keynames.append(r[0])
                    continue
                if key_name in keys:
                    # Composite key part
                    keys[key_name]['_col_aliases'].append(r[1])
                    continue
                # Defining a new key
                key['constraint_name'] = key_name
                key['is_foreign_key'] = (key_type == 'FOREIGN KEY')
                key['referenced_table_name'] = None
                key['referenced_columns'] = []
                key['on_update'] = None
                key['on_delete'] = None
                key['_col_aliases'] = [r[1], ]
                keys[key_name] = key

        # Additionally selecting information about referential constraints - foreign keys. Doing it
        # by selecting from REFERENTIAL_CONSTRAINTS basing on PostgreSQL documentation
        # "34.32 The Information Schema.referential_constraints"
        # Note that PostgreSQL gives no posibility to filter referential_constraints table againts
        # specific table name and returns all constraints for the database at a time.
        query = ("SELECT CONSTRAINT_NAME, UPDATE_RULE, DELETE_RULE FROM"
                 " INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS WHERE"
                 " CONSTRAINT_SCHEMA = %(ts)s")
        dbr = self.query(query, {'ts': self.dbms_schema}).all()
        if dbr:
            for r in dbr:
                fk_name = r[0]
                if fk_name not in keys:
                    continue
                keys[fk_name]['is_foreign_key'] = True
                keys[fk_name]['on_update'] = r[1]
                keys[fk_name]['on_delete'] = r[2]

        # Handling got keys
        if keys:
            for name in keys:
                # We about to define three general types of keys:
                # a) PRIMARY KEY
                # b) FOREIGN KEY
                # c) UNIQUE KEY
                # INDEX KEY (or just a KEY in terms of PostgreSQL) are stored
                # separatelly, so will not be found in general KEYS structure.
                # The first type (a) - the PRIMARY KEY (even composite)
                # detects in the procedure above and not stored in the general
                # `keys` variable, so this is not a point to work with PK here.
                key = keys[name]
                is_fk = key['is_foreign_key']
                if is_fk:
                    # Due PostgreSQL does not stores information about foreign key referenced
                    # table and columns in the information schema with key column usage - we have
                    # to query for this information additionaly againts every FK constraint.
                    query = (
                        "SELECT TABLE_NAME, COLUMN_NAME"
                        " FROM INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE"
                        " WHERE CONSTRAINT_NAME=%(cn)s"
                    )
                    dbr = self.query(query, {'cn': key['constraint_name']}).all()
                    if dbr:
                        ref_tablename = None
                        ref_columns = []
                        for r in dbr:
                            ref_tablename = str(r[0])
                            ref_columns.append(str(r[1]))
                        key['referenced_table_name'] = ref_tablename
                        key['referenced_columns'] = ref_columns
                    fk = {
                        'constraint_name': key['constraint_name'],
                        'model_idx_columns': key['_col_aliases'],
                        'ref_idx_columns': key['referenced_columns'],
                        'ref_table': key['referenced_table_name'],
                        'on_update': key['on_update'],
                        'on_delete': key['on_delete']
                    }
                    foreign_keys[name] = fk
                else:
                    uk = {
                        'constraint_name': key['constraint_name'],
                        '_col_aliases': key['_col_aliases']
                    }
                    unique_keys[name] = uk

        # Selecting information about INDEX KEYs, basing on internal PostgreSQL functionality.
        # Too bad, but this information is not accessible from standard schema (from
        # INFORMATION SCHEMA), so we have to use PostgreSQL specific way only.
        query = ("SELECT ix.relname, regexp_replace(pg_get_indexdef(indexrelid), '.*\\((.*)\\)', '\\1')"
                 " FROM pg_index i"
                 " JOIN pg_class t ON t.oid = i.indrelid"
                 " JOIN pg_class ix ON ix.oid = i.indexrelid"
                 " WHERE t.relname = %(tn)s")
        dbr = self.query(query, {'ts': self.dbms_schema, 'tn': tablename}).all()
        if dbr:
            for r in dbr:
                name = r[0]
                # If the index key is already registered in the `keys` varitable - skipping
                # due this is not a index key.
                if name in keys or name in pk_keynames:
                    continue
                indexes[name] = {
                    'key_name': name,
                    '_col_aliases': [],
                    'column_names': []
                }
                idx_columns = r[1].split(',')
                for cn in idx_columns:
                    indexes[name]['_col_aliases'].append((cn, None))
                    indexes[name]['column_names'].append(cn)

        # Accumulating the resulting information about model's table definition
        table_struct = {
            'columns': columns,
            'indexes': indexes,
            'foreign_keys': foreign_keys,
            'unique_keys': unique_keys,
            'primary_key': pk
        }
        return table_struct

    def is_model_table_exists(self, model):
        """ Checks is the OrmModel's table existance in the database.
        :model                      (OrmModel) The Model for which to search for database table
                                    existabce to;
        :returns                    True if the corresponding database table is exists, False
                                    otherwise.
        """
        q = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = %(ts)s AND TABLE_NAME = %(tn)s"
        r = self.query(q, {'tn': self.dbms_schema, 'ts': self.dbms_dbname}).one()
        if not r:
            return False
        return str(r[0]) == str(model.table)

    def create_model_table(self, model, apply=True, restrict_new_fk=False):
        """ Creates a table in the database. Raises an exeption if the table is already
        exists in the database. Use `alter` instead to automatically migrate the database
        schema (do create or alter the table).
        :model                      (OrmModel) The corresponding Model for which database table to
                                    create to;
        :apply                      [bool] If set to True - automatically executes the ALTER query,
                                    if not - only returns the SQL query;
        :restrict_new_fk            [bool] If set to True - foreign keys will not be created right
                                    after database table creation; otherwise (default) - corresponding
                                    CREATE FOREIGN KEY procedures will be planned;
        :returns                    (str) Resulting SQL query.
        """
        if self.is_model_table_exists(model):
            raise Exception("Cannot CREATE TABLE because it is already exists: \"%s\"" % model.table)
        columns = model.__meta__.get_column_attributes()
        c_def = []
        for c in columns:
            q = c.declaration_sql(self)
            c_def.append("\"%s\" %s" % (c.tbl_k, q))
        q_def = ", ".join(c_def)
        if model.__meta__.primary_key:
            pkc = []
            for c in model.__meta__.get_primary_key():
                pkc.append("\"%s\"" % c.tbl_k)
            q_pk = "PRIMARY KEY (%s)" % (", ".join(pkc))
            q_def += ", " + q_pk
        foreign_keys = model.__meta__.get_foreign_keys()
        if foreign_keys and not restrict_new_fk:
            fks = []
            for fk in foreign_keys:
                fks.append(fk.declaration_sql(self))
            q_fk = ", ".join(fks)
            q_def += ", " + q_fk
        unique_keys = model.__meta__.get_unique_keys()
        if unique_keys:
            uks = []
            for uk in unique_keys:
                uks.append(uk.declaration_sql(self))
            q_uk = ", ".join(uks)
            q_def += ", " + q_uk
        #
        # PostgreSQL cannot create or alter indexes within table definition or modification,
        # it uses separate 'CREATE INDEX', 'ALTER INDEX' AND 'DROP INDEX' procedures, so them must
        # be handled separatelly, not within main query.
        # index_keys = model.__meta__.get_index_keys()
        #
        # if index_keys:
        #     iks = []
        #     for ik in index_keys:
        #         iks.append(ik.declaration_sql(self))
        #     q_ik = ", ".join(iks)
        #     q_def += ", " + q_ik
        query = "CREATE TABLE \"%s\" (%s)" % (model.table, q_def)
        if apply:
            self.execute(query)
        return query

    def alter_model_table(self, model, table_struct=None, drop=False, alter_foreign_keys=True):
        """ Returns a SQL query to alter database table basing on the declared Model.
        :model                      (OrmModel) the Model for which corresponding
                                    database table to alter;
        :table_struct               [dict] containing the current corresponding table structure
                                    at the database; if not set - current table structure will
                                    be automatically loaded by this method;
        :drop                       [bool] If set to True - columns in the database table which
                                    are not exists in the Model will be dropped; otherwise
                                    (default) - will be kept not touched;
        :alter_foreign_keys         [bool] If set to True (default) - foreign keys will be altered
                                    right in place of this alter procedure; otherwise this method
                                    will not worry about dropping and creating foreign keys;
        :returns                    (str) The resulting query.
        """
        if not table_struct:
            table_struct = self.get_table_struct(model.table)
        model_struct = model.__meta__.get_model_struct()

        _q_to_alter = []
        _fk_to_drop = []

        # Columns
        for k in model_struct['columns']:
            c = model_struct['columns'][k]
            tbl_k = c.tbl_k
            if not isinstance(c, ColumnAttributeAbstract):
                continue
            # If the column not exists at all - just add it in the alter procedure
            if tbl_k not in table_struct['columns']:
                add_sql = c.declaration_sql(self)
                q = "ADD \"%s\" %s" % (tbl_k, add_sql)
                _q_to_alter.append(q)
                continue
            # If the column exists - we have to compare it's model definition with
            # database table definition and make changes in the alter procedure
            # if some differences will be found.
            tbl_c = table_struct['columns'][tbl_k]
            if not c.is_eq_with_tbl_schema(tbl_c, self):
                alter_sql = c.alter_sql(self)
                if isinstance(alter_sql, (list, tuple)):
                    for q_ in alter_sql:
                        _q_to_alter.append("ALTER COLUMN \"%s\" %s" % (tbl_k, q_))
                else:
                    q = "ALTER COLUMN \"%s\" %s" % (tbl_k, alter_sql)
                    _q_to_alter.append(q)
                # Checking - is this column using in foreign keys - and mark those
                # foreign keys where this column is using to drop prior to the
                # column been modified.
                for fk_name in table_struct['foreign_keys']:
                    if fk_name in _fk_to_drop:
                        continue
                    key = table_struct['foreign_keys'][fk_name]
                    if tbl_k not in key['model_idx_columns']:
                        continue
                    _fk_to_drop.append(fk_name)

        # Primary key
        t_pk = table_struct['primary_key']
        m_pk = model_struct['primary_key']
        if not compare_keys(t_pk, m_pk):
            cs = []
            for c in m_pk:
                cs.append("\"%s\"" % str(c.tbl_k))
            q = "" if not t_pk else "DROP PRIMARY KEY, "
            q += "ADD PRIMARY KEY(%s)" % ",".join(cs)
            _q_to_alter.append(q)

        # Unique keys
        t_uks = table_struct['unique_keys']
        m_uks = model_struct['unique_keys']
        keep_uks = []
        add_uks = []
        for k in m_uks:
            m_key = m_uks[k]
            if m_key.tbl_k not in t_uks:
                add_uks.append(m_key)
                continue
            t_key = t_uks[m_key.tbl_k]
            if not compare_keys(t_key['_col_aliases'], m_key.columns):
                add_uks.append(m_key)
            else:
                keep_uks.append(m_key.tbl_k)
        for tbl_k in t_uks:
            if tbl_k in keep_uks:
                continue
            q = "DROP CONSTRAINT \"%s\"" % str(tbl_k)
            _q_to_alter.append(q)
        for c in add_uks:
            _q_to_alter.append("ADD %s" % c.declaration_sql(self))

        # Index keys
        #
        # PostgreSQL cannot create or alter indexes within table definition or modification,
        # it uses separate 'CREATE INDEX', 'ALTER INDEX' AND 'DROP INDEX' procedures, so them must
        # be handled separatelly, not within main query.
        # index_keys = model.__meta__.get_index_keys()
        #
        # t_ixs = table_struct['indexes']
        # m_ixs = model_struct['indexes']
        # keep_ixs = []
        # add_ixs = []
        # for k in m_ixs:
        #     m_key = m_ixs[k]
        #     if m_key.tbl_k not in t_ixs:
        #         add_ixs.append(m_key)
        #         continue
        #     t_key = t_ixs[m_key.tbl_k]
        #     if not compare_keys(t_key['column_names'], m_key.columns):
        #         add_ixs.append(m_key)
        #     else:
        #         keep_ixs.append(m_key.tbl_k)
        # for tbl_k in t_ixs:
        #     if tbl_k in keep_ixs:
        #         continue
        #     q = "DROP KEY `%s`" % str(tbl_k)
        #     _q_to_alter.append(q)
        # for c in add_ixs:
        #     _q_to_alter.append("ADD %s" % c.declaration_sql(self))

        # Foreign keys
        t_fks = table_struct['foreign_keys']
        m_fks = model_struct['foreign_keys']
        keep_fks = []
        add_fks = []
        for k in m_fks:
            m_key = m_fks[k]
            m_key.validate()
            if m_key.tbl_k not in t_fks or m_key.tbl_k in _fk_to_drop:
                add_fks.append(m_key)
                continue
            t_key = t_fks[m_key.tbl_k]
            if t_key['ref_table'] != m_key.ref_model.table \
                    or len(t_key['model_idx_columns']) != len(m_key.columns) \
                    or len(t_key['ref_idx_columns']) != len(m_key.ref_columns):
                add_fks.append(m_key)
                continue
            do_continue = False
            for i in xrange(len(m_key.columns)):
                if t_key['model_idx_columns'][i] == getattr(m_key.model, m_key.columns[i]).tbl_k:
                    continue
                add_fks.append(m_key)
                do_continue = True
                break
            if do_continue:
                continue
            for i in xrange(len(m_key.ref_columns)):
                if t_key['ref_idx_columns'][i] == getattr(m_key.ref_model, m_key.ref_columns[i]).tbl_k:
                    continue
                add_fks.append(m_key)
                do_continue = True
                break
            if do_continue:
                continue
            t_key_on_delete = str(t_key['on_delete']).upper()
            if t_key_on_delete in ('NO ACTION', 'RESTRICT'):
                t_key_on_delete = 'RESTRICT'
            m_key_on_delete = 'RESTRICT' if m_key.on_delete is None else str(m_key.on_delete).upper()
            if t_key_on_delete != m_key_on_delete:
                add_fks.append(m_key)
                continue
            t_key_on_update = str(t_key['on_update']).upper()
            if t_key_on_update in ('NO ACTION', 'RESTRICT'):
                t_key_on_update = 'RESTRICT'
            m_key_on_update = 'RESTRICT' if m_key.on_update is None else str(m_key.on_update).upper()
            if t_key_on_update != m_key_on_update:
                add_fks.append(m_key)
                continue
            keep_fks.append(m_key.tbl_k)
        for tbl_k in t_fks:
            if tbl_k in keep_fks or tbl_k in _fk_to_drop:
                continue
            _fk_to_drop.append(tbl_k)
        need_alter_foreign_keys = len(add_fks) != 0
        if alter_foreign_keys:
            for c in add_fks:
                _q_to_alter.append("ADD %s" % c.declaration_sql(self))

        # If nothing to do - just returning None
        if not _q_to_alter and not _fk_to_drop:
            return None

        queries = list()
        # If we have foreign keys to be dropped prior to other ALTER actions,
        # including adding changed version of those foreign keys - put drops
        # in front of all other actions here
        if _fk_to_drop and alter_foreign_keys:
            q_fk_drop = []
            for fk_name in _fk_to_drop:
                q_fk_drop.append("DROP CONSTRAINT \"%s\"" % str(fk_name))
            dfk_query = "ALTER TABLE \"%s\" %s" % (model.table, ", ".join(q_fk_drop))
            queries.append(dfk_query)

        # Composing SQL ALTER request
        query = "ALTER TABLE \"%s\" %s" % (model.table, ", ".join(_q_to_alter)) if _q_to_alter else ""
        if query:
            queries.append(query)

        # If only we need - is to alter foreign keys
        if not queries and need_alter_foreign_keys:
            return True

        # Returning prepared queries
        return queries

    def create_model_foreign_keys(self, model):
        """ Returns a SQL query to create foreign keys for the database table
        basing on the declared Model.
        :model                      (OrmModel) the Model for which corresponding
                                    database table to create foreign keys for;
        :returns                    (str) The resulting query.
        """
        query = ""
        foreign_keys = model.__meta__.get_foreign_keys()
        if foreign_keys:
            fks = []
            for fk in foreign_keys:
                fks.append("ADD %s" % fk.declaration_sql(self))
            query = ", ".join(fks)
        if query:
            query = "ALTER TABLE \"%s\" %s" % (model.table, query)
        return query

    def drop_table_foreign_keys(self, tablename, tbl_struct_fks):
        """ Returns a SQL query to drop foreign keys for the database table.
        :tablename                  (str) The name of the datbase table;
        :tbl_struct_fks             (dict) Existing foreign keys struct;
        :returns                    (str) The resulting query.
        """
        if not tbl_struct_fks:
            return None
        queries = list()
        for fk_name in tbl_struct_fks:
            constraint_name = tbl_struct_fks[fk_name]['constraint_name']
            queries.append("DROP CONSTRAINT \"%s\"" % str(constraint_name))
        return "ALTER TABLE \"%s\" %s" % (tablename, ", ".join(queries))

    def drop_model_table(self, model, apply=True):
        """ Drops the model's table from the database.
        :apply          (bool) If set_value to True - automatically executes the ALTER query, if
                        not - only returns the SQL query.
        :returns        (str) SQL query for DROPing the table.
        """
        if not self.is_model_table_exists(model):
            raise Exception("Cannot DROP table because it is not exists: `%s`!" % model.__table__)
        pass

    def get_database_tables(self):
        """
        :returns                    (list) A list of table names in the current database.
        """
        q = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '%s'" % self.dbms_schema
        dbr = self.query(q).all()
        existing_tables = []
        for r in dbr:
            existing_tables.append(r[0])
        return existing_tables

