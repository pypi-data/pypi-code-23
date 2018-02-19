import click
import os
import pymysql
from configparser import ConfigParser, NoSectionError
from amaasinfra.config.amaas_config import AMaaSConfig

class DatabaseSetter(object):
    def __init__(self, sql_dir=None):
        self.sql_dir = os.path.realpath(sql_dir) if sql_dir else os.getcwd()

    def recreate(self, schema, environment, db_config=None):
        db_config = db_config or {}
        server = username = password = None

        # Try to load settings
        if environment == 'local':
            click.echo("Using Local Settings")
            server = "localhost"
            username = "root"
            password = "amaas"
        else:
            try:
                config = AMaaSConfig()
            except Exception:
                pass
            else:
                click.echo("Loading file config")
                section = 'stages.{}'.format(environment)
                try:
                    server = config.get_config_value(section, 'db_server')
                    username = config.get_config_value(section, 'db_username')
                    password = config.get_config_value(section, 'db_password')
                except Exception:
                    # Legacy format
                    try:
                        server = config.get_config_value(environment, 'db_server')
                        username = config.get_config_value(environment, 'db_username')
                        password = config.get_config_value(environment, 'db_password')
                    except Exception:
                        pass

        server = db_config.get('db_server', server)
        username = db_config.get('db_username', username)
        password = db_config.get('db_password', password)

        click.echo("Settings: server={}, username={}, password={}".format(
            server, username, '*' * len(password),
        ))

        if any(s is None for s in (server, username, password)):
            msg = 'Unable to find database settings for environment {!r}'
            raise Exception(msg.format(environment))

        # Connect to the server and create database
        try:
            click.echo("Connecting to the server")
            conn = pymysql.connect(server, user=username, passwd=password, charset='utf8')
            cur = conn.cursor()
            cur.execute("SET time_zone = '+00:00';")
            click.echo("Creating schema: " + schema)
            cur.execute("DROP DATABASE IF EXISTS " + schema + ";")
            cur.execute("CREATE DATABASE " + schema + " CHARACTER SET utf8 COLLATE utf8_unicode_ci;")
            cur.execute("USE " + schema + ";")
            click.echo("Schema " + schema + " created successfully.")
        except (pymysql.InternalError, pymysql.OperationalError):
            raise Exception('Error Creating DB and Connection')

        tables_path = db_config.get('table_path',
                                    os.path.join(self.sql_dir, "tables"))
        data_path = db_config.get('data_path',
                                  os.path.join(self.sql_dir, "data"))

        files = [(f, tables_path) for f in os.listdir(tables_path)]
        if os.path.exists(data_path):
            files += [(f, data_path) for f in os.listdir(data_path)]
        # Execute sql files
        try:
            for file, path in files:
                if file in db_config.get('ignore', []):
                    continue

                file_path = os.path.join(path, file)
                with open(file_path) as sql_file:
                    click.echo("Reading: " + file_path)
                    content = sql_file.readlines()
                exe_line = ''
                for line in content:
                    exe_line += line.partition('#')[0].rstrip()
                    if exe_line != '' and str(exe_line[-1]) == ';':
                        click.echo("Executing: " + exe_line)
                        conn.cursor().execute(exe_line)
                        exe_line = ''
                click.echo("Ran SQL: " + file[:-4] + " successfully")
            conn.commit()
        except pymysql.OperationalError:
            raise Exception('Error executing mysql files in tables')
