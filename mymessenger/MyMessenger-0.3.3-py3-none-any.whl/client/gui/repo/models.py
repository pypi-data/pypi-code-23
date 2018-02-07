import os
from sqlalchemy import Column, Integer, String, BLOB, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


class ClientInfo(Base):
    __tablename__ = 'ClientInfo'
    Key = Column(String, primary_key=True)
    Value = Column(String)

    def __init__(self, key, value):
        self.Key = key
        self.Value = value

    def __repr__(self):
        return '<ClientInfo ({}: {})>'.format(self.Key, self.Value)


class Image(Base):
    __tablename__ = 'image'
    id = Column(Integer, primary_key=True)
    Data = Column(BLOB)


DB_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_FOLDER_PATH, 'client.db')
engine = create_engine('sqlite:///{}'.format(DB_PATH), echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
session = session
