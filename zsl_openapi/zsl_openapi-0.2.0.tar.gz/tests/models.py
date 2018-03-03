from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.sql.sqltypes import Integer
from sqlalchemy.sql.sqltypes import String
from zsl.db.model.sql_alchemy import DeclarativeBase


class User(DeclarativeBase):
    __tablename__ = 'user'
    __table_args__ = {'useexisting': True}

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    created = Column(DateTime(), nullable=False)
