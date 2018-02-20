import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base


def get_db_conn():
    host = os.environ.get('db_host')
    name = os.environ.get('db_name')
    user = os.environ.get('db_user')
    password = os.environ.get('db_password')
    engine = create_engine(
        'postgresql://{user}:{password}@{host}/{db}'.format(user=user, password=password, host=host, db=name)
    )
    return engine

def get_engine_and_base():
    engine = get_db_conn()
    existing_base = automap_base()
    existing_base.prepare(engine, reflect=True)
    return engine, existing_base


def get_session(engine=None):
    if not engine:
        engine = get_db_conn()
    return Session(engine)

