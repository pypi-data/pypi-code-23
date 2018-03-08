from sqlalchemy import Column, String, Integer, Boolean, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# FIXME: remove ts3ekkoclient dependency for fixture seed
# gotta come up with a solution for this one at some point, but this one is enough for now
# This import is needed, because the ts3ekkomanager seeds the database with the permission starting configuration.
# I chose to introduce this dependency instead of outsourcing the code into the ts3ekkoutil module, because the util module would require an update, even if only a property of a model changed (not an actual attribute)
from ts3ekkoclient.models import PermissionGrant, PermissionServerGroups, PermissionDoc


def create_ts3ekkoclient_tables(username, password, dbhost, dbname):
    from ts3ekkoclient.models import Base as ekkoclient_base
    ekkoclient_engine = create_engine(f'postgres://{username}:{password}@{dbhost}/{dbname}')
    ekkoclient_base.metadata.create_all(ekkoclient_engine)


Base = declarative_base()


class Identity(Base):
    __tablename__ = 'identity'
    eid = Column(Integer, Sequence('identity_id_seq', start=1001, increment=1), primary_key=True)
    unique_ts3_id = Column(String(50), nullable=False, unique=True)
    private_identity = Column(String(300), nullable=False, unique=True)


def startup(username='ekko', password='ekkopassword', dbhost='dbhost', dbname='ekkodb'):
    create_ts3ekkoclient_tables(username, password, dbhost, dbname)

    engine = create_engine(f'postgres://{username}:{password}@{dbhost}/{dbname}')

    Base.metadata.create_all(engine)

    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)

    session = DBSession()
    return session
