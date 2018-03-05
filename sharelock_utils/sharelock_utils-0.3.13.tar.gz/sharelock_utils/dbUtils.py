import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.pool import NullPool


def get_db_conn(null_pool=False):
    host = os.environ.get('db_host')
    name = os.environ.get('db_name')
    user = os.environ.get('db_user')
    password = os.environ.get('db_password')
    full_path = 'postgresql://{user}:{password}@{host}/{db}'.format(user=user, password=password, host=host, db=name)
    if null_pool:
        engine = create_engine(full_path, poolclass=NullPool)
    else:
        engine = create_engine(full_path)
    return engine


def get_engine_and_base(null_pool=False):
    engine = get_db_conn(null_pool)
    existing_base = automap_base()
    existing_base.prepare(engine, reflect=True)
    return engine, existing_base


def get_session(engine=None):
    if not engine:
        engine = get_db_conn()
    return Session(engine)

