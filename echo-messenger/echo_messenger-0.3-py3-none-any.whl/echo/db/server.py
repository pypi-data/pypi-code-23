import time
import os
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

contact_table = Table('contact', Base.metadata,
                      Column('client_id', Integer, ForeignKey('client.id')),
                      Column('contact_id', Integer, ForeignKey('client.id'))
                      )


class Client(Base):
    __tablename__ = 'client'
    id = Column(Integer, primary_key=True)
    email = Column(String)
    name = Column(String)
    history = relationship('History', back_populates='client')
    contacts = relationship('Client', secondary=contact_table,
                            backref='owner',
                            primaryjoin=id == contact_table.c.client_id,
                            secondaryjoin=id == contact_table.c.contact_id
                            )

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Client ({})>'.format(self.name)


class History(Base):
    __tablename__ = 'history'
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('client.id'))
    ip = Column(String)
    timestamp = Column(String)
    client = relationship('Client', back_populates='history')

    def __init__(self, client, ip):
        self.ip = ip
        self.client = client
        self.timestamp = time.time()

    def __repr__(self):
        return '<History ({})>'.format(self.ip)


engine = create_engine('sqlite:///{}'.format(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'server.db')), echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()