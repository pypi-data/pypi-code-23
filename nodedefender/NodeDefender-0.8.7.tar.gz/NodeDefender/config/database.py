import NodeDefender
import flask_migrate
import sqlalchemy
import os
from flask_sqlalchemy import SQLAlchemy
import alembic
import shutil
default_config = {'enabled' : False,
                  'engine' : '',
                  'username' : '',
                  'password' : '',
                  'host' : '',
                  'port' : '',
                  'database' : '',
                  'filepath' : ''}

config = default_config.copy()

def load_config(parser):
    config['enabled'] = eval(parser['DATABASE']['ENABLED'])
    config['engine'] = parser['DATABASE']['ENGINE']
    config['username'] = parser['DATABASE']['USERNAME']
    config['password'] = parser['DATABASE']['PASSWORD']
    config['host'] = parser['DATABASE']['HOST']
    config['port'] = parser['DATABASE']['PORT']
    config['database'] = parser['DATABASE']['DATABASE']
    config['filepath'] = parser['DATABASE']['FILEPATH']
    NodeDefender.app.config.update(
        DATABASE=config['enabled'],
        DATABASE_ENGINE=config['engine'],
        DATABASE_USERNAME=config['username'],
        DATABASE_PASSWORD=config['password'],
        DATABASE_HOST=config['host'],
        DATABASE_PORT=config['port'],
        DATABASE_DATABASE=config['database'],
        DATABASE_FILEPATH=config['filepath'])
    if NodeDefender.app.testing:
        NodeDefender.app.config.update(
            SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:")
    else:
        NodeDefender.app.config.update(
            SQLALCHEMY_DATABASE_URI = get_uri())
    return config

def test_database():
    app = NodeDefender.app
    app.config.update(
        SQLALCHEMY_DATABASE_URI = get_uri())
    db = NodeDefender.db.sql.load(app)
    '''
    app = NodeDefender.factory.CreateApp()
    app.config.update(SQLALCHEMY_DATABASE_URI = get_uri())
    db = NodeDefender.db.sql.load(app)
    '''

    folder = NodeDefender.config.migrations_folder
    migrate = flask_migrate.Migrate(app, db, folder)
    try:
        init_migrations(app)
    except alembic.util.exc.CommandError:
        drop_alembic_table(db)
        remove_migrations_folder(folder)
        init_migrations(app)
    
    try:
        migrate_database(app)
        upgrade_database(app)
    except Exception:
        pass

    return True

def drop_alembic_table(db):
    query = sqlalchemy.text("drop table alembic_version")
    try:
        db.engine.execute(query)
    except Exception:
        pass
    return True

def remove_migrations_folder(folder):
    try:
        shutil.rmtree(folder)
    except FileNotFoundError:
        pass
    return True

def init_migrations(app):
    with app.app_context():
        flask_migrate.init()

def migrate_database(app):
    with app.app_context():
        flask_migrate.migrate()

def upgrade_database(app):
    with app.app_context():
        flask_migrate.upgrade()

def get_uri():
    if config['engine'] == 'sqlite':
        return 'sqlite:///' + config['filepath']
    username = config['username']
    password = config['password']
    host = config['host']
    port = config['port']
    database = config['database']
    if config['engine'] == 'mysql':
        return 'mysql+pymysql://'+username+':'+password+'@'+host+':'+port+\
            '/'+database
    elif config['engine'] == 'postgresql':
        return 'postgresql://'+username+':'+password+'@'+host+':'+port+\
                '/'+database()
    return "sqlite:///:memory:"

def set_default():
    for key, value in default_config.items():
        NodeDefender.config.parser['DATABASE'][key] = str(value)
    return True

def set(**kwargs):
    for key, value in kwargs.items():
        if key not in config:
            continue
        if key == "filepath":
            value = os.path.join(NodeDefender.config.datafolder, value)
        config[key] = str(value)
    test_database()
    return True

def write():
    NodeDefender.config.parser['DATABASE'] = config
    NodeDefender.config.write()
