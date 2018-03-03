from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.schema import Table
from sqlalchemy.sql.sqltypes import Integer
from sqlalchemy.sql.sqltypes import String
from zsl.db.model.sql_alchemy import DeclarativeBase

customer_client_table = Table('customer_client', DeclarativeBase.metadata,
                              Column('customer_id', Integer, ForeignKey('user2.id'), nullable=False),
                              Column('client_id', Integer, ForeignKey('user2.id'), nullable=False)
                              )


class User2(DeclarativeBase):
    __tablename__ = 'user2'
    __table_args__ = {'useexisting': False}

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)

    clients = relationship("User2", secondary=customer_client_table, back_populates='customers',
                           primaryjoin=(customer_client_table.c.client_id == id),
                           secondaryjoin=(customer_client_table.c.customer_id == id))
    customers = relationship("User2", secondary=customer_client_table, back_populates="clients",
                             primaryjoin=(customer_client_table.c.customer_id == id),
                             secondaryjoin=(customer_client_table.c.client_id == id))
