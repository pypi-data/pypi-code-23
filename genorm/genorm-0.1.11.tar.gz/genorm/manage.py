from os import makedirs
from os.path import lexists
from inspect import isclass
from .exceptions import OrmManagementError, OrmAttributeTypeMistake
from .storages import OrmFileStorage, OrmPictureStorage


class OrmManager(object):
    def __init__(self):
        self._debug = False
        self._sessions = {}
        self._userident = None
        self._storages = {
            None: {}
        }
        self._journals = {
            None: {}
        }
        self._query_handler = None
        self._model_request_handler = None
        self._model_write_handler = None
        self._gettext = None
        self._storage_base_path = None
        self._logs = {}
        self._telephony = {
            'formats': {
                6: '??-??-??',
                7: '???-??-??',
                10: '(???) ???-??-??',
                11: '+? (???) ???-??-??',
                12: '+?? (???) ???-??-??',
                13: '+??? (???) ???-??-??',
                14: '+?-??? (???) ???-??-??',
            },
            'format_ext': ' (+?)',
            'local_prefixes': {},
        }
        self._finances = {
            'currency_formats': {
                'rur': ('%irub. %dkop.', '%i rub.'),
                'usd': ('$%i.%d', '$%i'),
                'eur': ('%i.%d EURO', '%i EURO')
            },
            'default_currency': False,
        }
        self._datetime_format = {
            'full_date': '%d.%m.%Y',
            'short_date': '%j.%m.%y',
            'full_time': '%H:%i:%s',
            'short_time': '%H:%i'
        }

    def set_debug(self, *args):
        if not args:
            self._debug = False
            return
        if True in args:
            self._debug = True
            return
        elif False in args:
            self._debug = False
            return
        d_ = list()
        for arg in args:
            if not isinstance(arg, str) \
                    or arg.lower() not in ('select', 'modify', 'alter', 'migrate-getstruct', 'query-results'):
                raise OrmManagementError(
                    "set_debug() requires value to be True, False, or a set of actions to debug to: 'select',"
                    " 'modify', 'alter', 'migrate-getstruct'!"
                )
            d_.append(arg.lower())
        self._debug = ",".join(d_)

    def get_debug(self):
        return bool(self._debug) if isinstance(self._debug, bool) else str(str(self._debug) + "!")

    def _get_managing_session(self, server_type, host, admin_username, admin_password, port=None, debug=None):
        if server_type == 'mysql':
            root_database = 'mysql'
        elif server_type == 'postgresql':
            root_database = 'postgres'
        else:
            raise OrmManagementError("server_type must be 'mysql' or 'postgresql'!")
        kw = {
            'server': server_type,
            'dbname': root_database,
            'username': admin_username,
            'password': admin_password,
            'host': host,
            'port': port,
            'debug': debug
        }
        return self.connect_db(**kw)

    @staticmethod
    def connect_mysql(*args, **kwargs):
        from .session import MysqlSession
        return MysqlSession(*args, **kwargs)

    @staticmethod
    def connect_postgresql(*args, **kwargs):
        from .session import PostgresqlSession
        return PostgresqlSession(*args, **kwargs)

    def connect_db(self, *args, **kwargs):
        session_type = kwargs.pop('server', None)
        if not isinstance(session_type, str) or str(session_type).lower() not in ('mysql', 'postgresql'):
            raise OrmManagementError("'server' parameter must be set and be one of 'mysql' or 'postgresql'!")
        if session_type.lower() == 'mysql':
            return self.connect_mysql(*args, **kwargs)
        elif session_type.lower() == 'postgresql':
            return self.connect_postgresql(*args, **kwargs)
        return None

    def is_database_exists(self, database_name, server_type, host, admin_username, admin_password, port=None,
                           session=None, debug=None):
        session_ = session \
                   or self._get_managing_session(server_type, host, admin_username, admin_password, port, debug)
        is_migrating = session_.is_migrating
        session_.is_migrating = True
        r = False
        if server_type == 'mysql':
            dbr = session_.query(
                "SELECT COUNT(1) FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = %(dbname)s",
                {'dbname': database_name}).one()
            r = bool(dbr[0])
        elif server_type == 'postgresql':
            dbr = session_.query(
                "SELECT COUNT(1) FROM pg_database WHERE datname = %(dbname)s",
                {'dbname': database_name}).one()
            r = bool(dbr[0])
        if session is None:
            session_.close()
        session_.is_migrating = is_migrating
        return r

    def drop_database(self, database_name, server_type, host, admin_username, admin_password, port=None, session=None,
                      just_ensure=False, debug=None):
        session_ = session \
                   or self._get_managing_session(server_type, host, admin_username, admin_password, port, debug)
        if session_.dbms_type == 'postgresql':
            from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
            session_.cn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        if self.is_database_exists(database_name=database_name, server_type=server_type, host=host,
                                   admin_username=admin_username, admin_password=admin_password, port=port,
                                   session=session_):
            session_.execute("DROP DATABASE %s" % session_.quote_name(database_name))
        elif not just_ensure:
            raise OrmManagementError("cannot drop database '%s' - is not exists!" % database_name)
        session_.commit()
        if session is None:
            session_.close()

    def create_database(self, database_name, server_type, host, admin_username, admin_password, port=None,
                        session=None, just_ensure=False, debug=None):
        session_ = session \
                   or self._get_managing_session(server_type, host, admin_username, admin_password, port, debug)
        if session_.dbms_type == 'postgresql':
            from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
            session_.cn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        if not self.is_database_exists(database_name=database_name, server_type=server_type, host=host,
                                       admin_username=admin_username, admin_password=admin_password, port=port,
                                       session=session_):
            if server_type == 'mysql':
                session_.execute("CREATE DATABASE `%s` CHARACTER SET utf8 COLLATE utf8_bin" % database_name)
            else:
                session_.execute("CREATE DATABASE %s" % session_.quote_name(database_name))
        elif not just_ensure:
            raise OrmManagementError("cannot create database '%s' - is already exists!" % database_name)
        session_.commit()
        if session is None:
            session_.close()

    def recreate_database(self, database_name, server_type, host, admin_username, admin_password, port=None,
                          session=None, debug=None):
        session_ = session \
                   or self._get_managing_session(server_type, host, admin_username, admin_password, port, debug)
        self.drop_database(database_name=database_name, server_type=server_type, host=host,
                           admin_username=admin_username, admin_password=admin_password, port=port, session=session_,
                           just_ensure=True, debug=debug)
        self.create_database(database_name=database_name, server_type=server_type, host=host,
                             admin_username=admin_username, admin_password=admin_password, port=port, session=session_,
                             just_ensure=True, debug=debug)
        if session is None:
            session_.close()

    def ensure_database(self, database_name, server_type, host, admin_username, admin_password, port=None,
                        session=None, debug=None):
        session_ = session \
                   or self._get_managing_session(server_type, host, admin_username, admin_password, port, debug)
        self.create_database(database_name=database_name, server_type=server_type, host=host,
                             admin_username=admin_username, admin_password=admin_password, port=port, session=session_,
                             just_ensure=True, debug=debug)
        if session is None:
            session_.close()

    def grant_permissions(self, database_name, server_type, host, admin_username, admin_password,
                          user_name, user_password, user_host=None, grant=None, schema='public', port=None,
                          session=None, debug=None):
        session_ = session \
                   or self._get_managing_session(server_type, host, admin_username, admin_password, port, debug)

        if session_.dbms_type == 'postgresql':
            from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
            session_.cn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        if not self.is_database_exists(database_name=database_name, server_type=server_type, host=host,
                                       admin_username=admin_username, admin_password=admin_password, port=port,
                                       session=session_):
            raise OrmManagementError(
                "Cannot grant permissions to database '%s' because it is not exists" % database_name
            )
        if not user_name or not user_password:
            raise OrmManagementError("grant_permissions() requires 'user_name' and 'user_password' to be set!")
        if server_type == 'mysql':
            if not grant:
                grant = 'ALL'
            if not user_host:
                user_host = "localhost"
            session_.execute("GRANT " + grant + " ON `" + database_name +
                             "`.* TO %(user)s@%(host)s IDENTIFIED BY %(passwd)s",
                             {
                                 'grant': grant,
                                 'database': database_name,
                                 'user': user_name,
                                 'passwd': user_password,
                                 'host': user_host
                             })
            session_.commit()
        else:
            pg_role = session_.query("SELECT 1 FROM pg_roles WHERE rolname = %(rolname)s", {'rolname': user_name})
            if not pg_role:
                session_.execute("CREATE USER \"" + user_name + "\" WITH PASSWORD %(passwd)s",
                                 {'passwd': user_password})
            else:
                session_.execute("ALTER ROLE \"" + user_name + "\" WITH PASSWORD %(passwd)s",
                                 {'passwd': user_password})
            if not grant:
                grant = 'ALL'
            session_.execute("GRANT CONNECT, TEMPORARY ON DATABASE \"%s\" TO \"%s\"" % (database_name, user_name),
                             {'database': database_name, 'rolname': user_name})
            session_.commit()
            pg_sess = self.connect_postgresql(host, database_name, admin_username, admin_password, port, debug=debug)
            pg_sess.execute("GRANT %s ON ALL TABLES IN SCHEMA \"%s\" TO \"%s\"" % (grant, schema, user_name))
            pg_sess.execute("GRANT %s ON ALL SEQUENCES IN SCHEMA \"%s\" TO \"%s\"" % (grant, schema, user_name))
            pg_sess.commit()

        if session is None:
            session_.close()

    def set_session_getter(self, f, tag=None):
        if not f or not callable(f):
            raise OrmManagementError("'set_session_getter' expects a function as parameter!")
        self._sessions[tag] = f

    def set_session(self, s, tag=None):
        from .session import OrmSessionAbstract
        if not isinstance(s, OrmSessionAbstract):
            raise OrmManagementError("'set_session' expects a DatabaseSession instance as parameter!")
        self._sessions[tag] = s

    def get_session(self, **kwargs):
        from .session import OrmSessionAbstract
        from .models.base import OrmModelAbstract

        tag_ = None

        session_ = kwargs.pop('session', None)
        if session_ is not None:
            if isinstance(session_, OrmSessionAbstract):
                return session_
            elif callable(session_):
                return session_()

        instance_ = kwargs.pop('instance', None)
        if instance_ is not None:
            if not isinstance(instance_, OrmModelAbstract):
                raise OrmAttributeTypeMistake(
                    "get_session(instance) parameter must be the type of OrmModel or not be set!"
                )
            if instance_.__session__ is not None:
                if isinstance(instance_.__session__, OrmSessionAbstract):
                    return instance_.__session__
                elif callable(instance_.__session__):
                    return instance_.__session__()

        model_ = kwargs.pop('model', None)
        if model_ is None and instance_ is not None:
            model_ = instance_.__class__
        if model_ is not None:
            if not issubclass(model_, OrmModelAbstract):
                raise OrmAttributeTypeMistake(
                    "get_session(model) parameter must be a class based on OrmModel class!"
                )
            if model_.__meta__.session is not None:
                if isinstance(model_.__meta__.session, OrmSessionAbstract):
                    return model_.__meta__.session
                elif callable(model_.__meta__.session):
                    return model_.__meta__.session()
            if model_.__meta__.tag is not None:
                tag_ = model_.__meta__.tag

        if tag_ not in self._sessions:
            return None
        if not self._sessions[tag_]:
            return None
        if isinstance(self._sessions[tag_], OrmSessionAbstract):
            return self._sessions[tag_]
        elif callable(self._sessions[tag_]):
            return self._sessions[tag_]()
        else:
            return None

    def set_user_ident(self, mixed):
        self._userident = mixed

    def get_user_ident(self):
        from .models.meta import OrmModelMeta
        from .models.base import OrmModel
        from .mapper import mapper
        ident = self._userident
        if ident is None and not mapper.is_userident_model_set():
            raise OrmManagementError("user ident must be set before using it in Models!")
        if ident is None:
            ident = mapper.get_userident_model()
        if callable(ident) and not isclass(ident):
            return ident()
        if issubclass(ident, OrmModelMeta) or issubclass(ident, OrmModel):
            return ident
        if isinstance(ident, str):
            model = mapper.get_model_by_name(ident)
            if model is None:
                raise OrmManagementError("user_ident model '%s' must be declared at a time of real queries!" % ident)
            return model
        raise OrmManagementError("user_ident might be set using callable function, Model or model name only!")

    def set_query_handler(self, f):
        if f is None:
            self._query_handler = None
            return
        if not callable(f):
            raise OrmManagementError("'set_query_handler' requires a callable function to be given!")
        self._query_handler = f

    def get_query_handler(self):
        return self._query_handler

    def clear_query_handler(self):
        self.set_query_handler(None)

    def handle_query(self, query, params):
        if not self._query_handler:
            return True
        return self._query_handler(query, params)

    def set_model_request_handler(self, f):
        if f is None:
            self._model_request_handler = None
            return
        if not callable(f):
            raise OrmManagementError("'set_model_request_handler' requires a callable function to be given!")
        self._model_request_handler = f

    def get_model_request_handler(self):
        return self._model_request_handler

    def clear_model_request_handler(self):
        self.set_model_request_handler(None)

    def handle_model_request(self, request):
        if not self._model_request_handler:
            return True
        return self._model_request_handler(request)

    def set_model_write_handler(self, f):
        if f is None:
            self._model_write_handler = None
            return
        if not callable(f):
            raise OrmManagementError("'set_model_write_handler' requires a callable function to be given!")
        self._model_write_handler = f

    def get_model_write_handler(self):
        return self._model_write_handler

    def clear_model_write_handler(self):
        self.set_model_write_handler(None)

    def handle_model_write(self, instance, is_extender, insert_ignore):
        if not self._model_write_handler:
            return True
        return self._model_write_handler(instance, is_extender=is_extender, insert_ignore=insert_ignore)

    def set_gettext(self, f):
        self._gettext = f

    def get_gettext_callback(self):
        return self._gettext

    def set_storage_base_path(self, path):
        self._storage_base_path = path
        if not lexists(path):
            makedirs(path)

    def get_storage_base_path(self):
        return self._storage_base_path

    def set_telephony_formats(self, formats):
        if formats is not None and not isinstance(formats, (list, tuple)):
            raise OrmManagementError("'set_telephony_formats' value must be a type of list or tuple!")
        formats_ = dict()
        for f in formats:
            fl = len(f) - len(f.replace('?', ''))
            formats_[fl] = f
        self._telephony['formats'] = formats_

    def update_telephony_formats(self, formats):
        if formats is not None and not isinstance(formats, (list, tuple)):
            raise OrmManagementError("'update_telephony_formats' value must be a type of list or tuple!")
        formats_ = dict()
        for f in formats:
            fl = len(f) - len(f.replace('?', ''))
            formats_[fl] = f
        for k in formats_:
            self._telephony['formats'][k] = formats_[k]

    def get_telephony_formats(self):
        return self._telephony['formats']

    def set_telephony_format_ext(self, format_ext):
        self._telephony['format_ext'] = format_ext

    def get_telephony_format_ext(self):
        return self._telephony['format_ext']

    def set_telephony_local_prefixes(self, prefixes):
        if not isinstance(prefixes, dict):
            raise OrmManagementError("'set_telephony_local_prefixes' requires value to be a type of (dict) in"
                                     " ({<base_length>: <prefix>, <base_length>: <prefix>})")
        prefixes_ = dict()
        for k in prefixes:
            if not isinstance(k, int):
                raise OrmManagementError("'set_telephony_local_prefixes' requires value to be a type of (dict) in"
                                         " ({<base_length>: <prefix>, <base_length>: <prefix>})")
            prefixes_[k] = str(prefixes[k])
        self._telephony['local_prefixes'] = prefixes_

    def update_telephony_local_prefixes(self, prefixes):
        if not isinstance(prefixes, dict):
            raise OrmManagementError("'set_telephony_local_prefixes' requires value to be a type of (dict) in"
                                     " ({<base_length>: <prefix>, <base_length>: <prefix>})")
        for k in prefixes:
            if not isinstance(k, int):
                raise OrmManagementError("'set_telephony_local_prefixes' requires value to be a type of (dict) in"
                                         " ({<base_length>: <prefix>, <base_length>: <prefix>})")
            self._telephony['local_prefixes'][k] = str(prefixes[k])

    def get_telephony_local_prefixes(self):
        return self._telephony['local_prefixes']

    def set_datetime_format(self, full_date=None, short_date=None, full_time=None, short_time=None):
        if full_date:
            self._datetime_format['full_date'] = str(full_date)
        if short_date:
            self._datetime_format['short_date'] = str(short_date)
        if full_time:
            self._datetime_format['full_time'] = str(full_time)
        if short_time:
            self._datetime_format['short_time'] = str(short_time)

    def get_datetime_formats(self):
        return self._datetime_format

    def get_full_date_format(self, session=None):
        return self._datetime_format['full_date'] if (session is None or session.dt_format is None) \
            else (session.dt_format['full_date'] or self._datetime_format['full_date'])

    def get_short_date_format(self, session=None):
        return self._datetime_format['short_date'] if (session is None or session.dt_format is None) \
            else (session.dt_format['short_date'] or self._datetime_format['short_date'])

    def get_full_time_format(self, session=None):
        return self._datetime_format['full_time'] if (session is None or session.dt_format is None) \
            else (session.dt_format['full_time'] or self._datetime_format['full_time'])

    def get_short_time_format(self, session=None):
        return self._datetime_format['short_time'] if (session is None or session.dt_format is None) \
            else (session.dt_format['short_time'] or self._datetime_format['short_time'])

    def set_default_currency(self, value):
        if not isinstance(value, str) and value is not False:
            raise OrmManagementError("'set_default_currency' requires (str) name of the currency!")
        self._finances['default_currency'] = value

    def set_currency_format(self, currency, full_format, integer_format):
        if not isinstance(currency, str) or not isinstance(full_format, str) or not isinstance(integer_format, str):
            raise OrmManagementError("currency name and formats must be a type of string!")
        self._finances['currency_formats'][currency] = (full_format, integer_format)

    def get_currency_format(self, currenty):
        if currenty not in self._finances['currency_formats']:
            return None
        return self._finances['currency_formats'][currenty]

    def get_default_currency(self):
        return self._finances['default_currency']

    def set_file_storage(self, name, base_path, tag=None, **kwargs):
        if tag not in self._storages:
            self._storages[tag] = dict()
        kwargs['base_path'] = base_path
        self._storages[tag][name] = OrmFileStorage(**kwargs)
        return self._storages[tag][name]

    def set_picture_storage(self, name, base_path, tag=None, **kwargs):
        if tag not in self._storages:
            self._storages[tag] = dict()
        kwargs['base_path'] = base_path
        self._storages[tag][name] = OrmPictureStorage(**kwargs)
        return self._storages[tag][name]

    def set_default_file_storage(self, base_path, tag=None, **kwargs):
        kwargs['base_path'] = base_path
        return self.set_file_storage('__defaultfilestorage__', tag=tag, **kwargs)

    def set_default_picture_storage(self, base_path, tag=None, **kwargs):
        kwargs['base_path'] = base_path
        return self.set_picture_storage('__defaultpicturestorage__', tag=tag, **kwargs)

    def set_default_storage(self, base_path, tag=None, **kwargs):
        kwargs['base_path'] = base_path
        kwargs['tag'] = tag
        self.set_default_file_storage(**kwargs)
        self.set_default_picture_storage(**kwargs)

    def get_storage(self, name, tag=None):
        if tag not in self._storages:
            raise OrmManagementError("tagged storage tree is not exists for tag: '%r'!" % tag)
        if name not in self._storages[tag]:
            raise OrmManagementError("storage is not exists: '%r'!" % name)
        return self._storages[tag][name]

    def get_default_file_storage(self, tag=None):
        return self.get_storage('__defaultfilestorage__', tag=tag)

    def get_default_picture_storage(self, tag=None):
        return self.get_storage('__defaultpicturestorage__', tag=tag)

    @staticmethod
    def _create_journal_model(name, tag=None):
        from .models.base import OrmModel
        from .models.templates import use_model_template
        from .logs import OrmJournalTemplate
        attrs = dict()
        if tag is not None:
            attrs['__tag__'] = tag
        return use_model_template(type(name, (OrmModel,), attrs), OrmJournalTemplate)

    def set_journal(self, name, tag=None, model=None, tablename=None):
        from .mapper import mapper
        from .models.base import OrmModel
        if tag in self._journals and name in self._journals[tag]:
            raise OrmManagementError("journal already exists with this tag: '%s'!" % name)
        if isinstance(model, str):
            model_ = mapper.get_model_by_name(model)
            if model_ is None:
                model_ = self._create_journal_model(model_)
        elif model is None:
            if name != '__default__':
                name_ = ("JournalLog_%s" % name) if tag is None else ("JournalLog_%s_%s" % (name, tag))
            else:
                name_ = "JournalLog" if tag is None else "JournalLog__%s" % tag
            model_ = self._create_journal_model(name_)
        elif issubclass(model, OrmModel):
            if not mapper.is_model_templated_with(model.__name__, 'OrmJournalTemplate'):
                raise OrmManagementError(
                    "Model which about to be used as journal must be declared using template OrmJournalTemplate!"
                )
            model_ = model
        else:
            raise OrmManagementError(
                "'set_journal' requires that 'model' parameter to be None or a type of Model or (str) - model name!"
            )
        model_.__meta__.tablename = tablename
        if tag not in self._journals:
            self._journals[tag] = dict()
        self._journals[tag][name] = model_

    def get_journal(self, name, tag=None):
        if tag not in self._journals or name not in self._journals[tag]:
            return None
        return self._journals[tag][name]

    def unset_journal(self, name, tag=None):
        from .mapper import mapper
        if not self.has_journal(name, tag):
            raise OrmManagementError("journal '%s' not been defined!" % name)
        model = self._journals[tag][name]
        mapper.unmap_model(model)

    def has_journal(self, name, tag=None):
        return tag in self._journals and name in self._journals[tag]

    def set_default_journal(self, tag=None, model=None, tablename=None):
        if self.has_journal('__default__', tag):
            self.unset_journal('__default__', tag)
        self.set_journal('__default__', tag, model, tablename)

    def get_default_journal(self, tag=None):
        return self.get_journal('__default__', tag)

    def unset_default_journal(self, tag=None):
        if not self.has_journal('__default__', tag):
            return
        self.unset_journal('__default__', tag)


manager = OrmManager()
